#!/usr/bin/env python3
"""Read NMEA GPS fixes from a serial device and optionally publish them to Firebase.

The script supports NMEA GGA sentences from modules such as the NEO-6M. It
prints each valid fix as decimal latitude/longitude and posts it only when a
Firebase URL is explicitly supplied. This keeps the module safe to import and
avoids coupling a checkout to a particular Firebase project.
"""

import argparse
from dataclasses import dataclass
from typing import Optional

import serial


@dataclass(frozen=True)
class GPSFix:
    """A valid GPS fix represented in decimal degrees."""

    timestamp: str
    latitude: float
    longitude: float


def nmea_coordinate_to_decimal(value: str, hemisphere: str) -> float:
    """Convert an NMEA ``ddmm.mmmm``/``dddmm.mmmm`` coordinate to decimal degrees."""
    if not value or hemisphere not in {"N", "S", "E", "W"}:
        raise ValueError("missing or invalid NMEA coordinate")

    raw = float(value)
    degrees = int(raw // 100)
    decimal = degrees + (raw - degrees * 100) / 60
    return -decimal if hemisphere in {"S", "W"} else decimal


def parse_gga(sentence: str) -> Optional[GPSFix]:
    """Parse a GGA sentence, returning ``None`` for a missing or invalid fix."""
    fields = sentence.strip().split(",")
    if len(fields) < 7 or not fields[0].endswith("GGA"):
        return None

    # GGA quality 0 means the receiver has no valid fix.
    if fields[6] == "0" or not fields[2] or not fields[4]:
        return None

    try:
        return GPSFix(
            timestamp=fields[1],
            latitude=nmea_coordinate_to_decimal(fields[2], fields[3]),
            longitude=nmea_coordinate_to_decimal(fields[4], fields[5]),
        )
    except ValueError:
        return None


def publish_fix(firebase_url: str, fix: GPSFix) -> None:
    """Publish a location update using the legacy python-firebase client."""
    from firebase import firebase  # Local parsing does not need Firebase configured.

    client = firebase.FirebaseApplication(firebase_url, None)
    client.post("/lati", fix.latitude)
    client.post("/long", fix.longitude)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", default="/dev/ttyS0", help="GPS serial device")
    parser.add_argument("--baudrate", type=int, default=9600, help="GPS serial baud rate")
    parser.add_argument(
        "--firebase-url",
        help="Firebase Realtime Database URL; omit to print fixes without uploading",
    )
    args = parser.parse_args()

    with serial.Serial(args.port, args.baudrate, timeout=1) as receiver:
        print(f"Reading GPS data from {args.port} at {args.baudrate} baud. Press Ctrl-C to stop.")
        try:
            while True:
                sentence = receiver.readline().decode("ascii", errors="replace")
                fix = parse_gga(sentence)
                if fix is None:
                    continue

                print(f"{fix.timestamp}: {fix.latitude:.6f}, {fix.longitude:.6f}")
                if args.firebase_url:
                    publish_fix(args.firebase_url, fix)
        except KeyboardInterrupt:
            print("\nStopped GPS telemetry.")


if __name__ == "__main__":
    main()
