# GoBot

**A Raspberry Pi rover prototype for autonomous item delivery, remote driving, perception, and live monitoring.**

GoBot brings together the pieces of a small robotic vehicle: camera streaming, TensorFlow Lite sign detection, GPIO-based motor/steering control, GPS telemetry, and resource monitoring. It is a hardware-focused prototype rather than a plug-and-play product; pin assignments, camera configuration, network addresses, and model labels must be adapted to the target vehicle.

## What it demonstrates

- **Perception-driven control** — runs a TensorFlow Lite model on a camera feed and uses detection confidence to stop or steer the rover.
- **Raspberry Pi actuation** — controls motor and steering signals through GPIO/PWM, including a Java/Pi4J TCP control server.
- **Live visibility** — serves an MJPEG camera stream and reports CPU, memory, and disk usage.
- **Location telemetry** — reads NMEA GPS data over serial and posts latitude/longitude to Firebase.

```text
Camera → TensorFlow Lite sign detection → GPIO/PWM → motors & steering
   │                                          │
   └────── MJPEG live stream                  └──── GPS + Firebase telemetry
```

## Repository map

| Area | Purpose |
| --- | --- |
| `Sign_detection/` | TensorFlow Lite camera inference and GPIO control loop. Includes a sample model and label dictionary. |
| `LandCruiser/` | Java/Pi4J TCP server and native steering experiments for Raspberry Pi hardware. |
| `picam.py` | Lightweight MJPEG web server for a Pi Camera stream on port `8000`. |
| `gps.py` | Serial NMEA GPS reader with Firebase location posting. |
| `Monitoring/monitoring.py` | CPU temperature, CPU, memory, and disk diagnostics using `psutil`. |

## Hardware and software assumptions

- Raspberry Pi with GPIO access and a compatible camera.
- A motor driver and steering servo wired to the GPIO pins configured in the scripts.
- Python 3, OpenCV, NumPy, TensorFlow or `tflite-runtime`, and `RPi.GPIO`.
- Optional: GPS module on `/dev/ttyS0`, Firebase project, and Pi4J for the Java control server.

The dependency file under `Sign_detection/` is a historical environment snapshot. For a new setup, install only the libraries required for the component you plan to run rather than the entire list.

## Quick start

> **Safety first:** keep the rover off the ground or disconnect its motor power while testing GPIO or perception code. Review every GPIO pin and PWM value before connecting hardware.

```bash
# Sign detection / camera control
cd Sign_detection
python3 TFLite_detection_webcam.py \
  --modeldir Sample_TFLite_model \
  --graph model.tflite \
  --labels dict.txt

# Pi Camera live stream
python3 picam.py
# Then open http://<raspberry-pi-address>:8000

# Device diagnostics
python3 Monitoring/monitoring.py
```

## Configuration notes

- Update GPIO pins, PWM duty cycles, and detection-index logic in `TFLite_detection_webcam.py` for the vehicle’s wiring and label order.
- Configure the serial device and Firebase endpoint in `gps.py` before enabling telemetry.
- `RCServer.java` listens on TCP port `4141`; it expects joystick/control values from a compatible client and requires Pi4J on the Pi.

## Status

This repository captures an early robotics prototype and its experiments. It is useful as a reference for the system architecture, but it has not been packaged or validated as a production deployment.

## Reference material

The original implementation drew on [Pi4J](https://www.pi4j.com/), [TensorFlow Lite](https://www.tensorflow.org/lite), [Firebase](https://firebase.google.com/), and Raspberry Pi camera-streaming examples.
