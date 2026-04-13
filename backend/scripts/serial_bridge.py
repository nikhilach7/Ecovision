import re
import time

import requests
import serial

SERIAL_PORT = "COM3"
BAUD_RATE = 9600
API_URL = "http://localhost:8000/api/sensor"
BIN_ID = "BIN-01"
LOCATION = "Campus Block A"
MAX_DEPTH_CM = 40

LINE_PATTERN = re.compile(r"Distance:\s*([0-9.]+)")


def main() -> None:
    print(f"Reading Arduino sensor data from {SERIAL_PORT}...")
    with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=2) as ser:
        time.sleep(2)
        while True:
            raw = ser.readline().decode("utf-8", errors="ignore").strip()
            if not raw:
                continue

            match = LINE_PATTERN.search(raw)
            if not match:
                continue

            distance_cm = float(match.group(1))
            payload = {
                "bin_id": BIN_ID,
                "distance_cm": distance_cm,
                "max_depth_cm": MAX_DEPTH_CM,
                "location": LOCATION,
            }

            try:
                response = requests.post(API_URL, json=payload, timeout=5)
                print(f"Distance {distance_cm}cm sent ({response.status_code})")
            except Exception as exc:
                print(f"Error posting sensor value: {exc}")


if __name__ == "__main__":
    main()
