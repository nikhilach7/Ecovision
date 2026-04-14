import re
import time

import requests
import serial

from app.core.config import settings
from app.services.thingspeak import build_thingspeak_payload, send_to_thingspeak

SERIAL_PORT = "COM3"
BAUD_RATE = 9600
API_URL = "http://localhost:8000/api/sensor"
BIN_ID = "BIN-01"
LOCATION = "Campus Block A"
MAX_DEPTH_CM = 40

LINE_PATTERN = re.compile(r"Distance:\s*([0-9.]+)")


def compute_metrics(distance_cm: float) -> tuple[float, float, int]:
    fill_level = round(max(0.0, min(100.0, (1 - (distance_cm / MAX_DEPTH_CM)) * 100)), 2)
    waste_level = round(100.0 - fill_level, 2)
    bin_status = 1 if fill_level > 90 else 0
    return fill_level, waste_level, bin_status


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
            fill_level, waste_level, bin_status = compute_metrics(distance_cm)
            payload = {
                "bin_id": BIN_ID,
                "distance_cm": distance_cm,
                "max_depth_cm": MAX_DEPTH_CM,
                "location": LOCATION,
            }

            try:
                response = requests.post(API_URL, json=payload, timeout=5)
                print(f"Distance {distance_cm}cm sent ({response.status_code})")
                if settings.thingspeak_is_enabled:
                    ts_payload = build_thingspeak_payload(
                        fill_level=fill_level,
                        waste_level=waste_level,
                        distance_cm=distance_cm,
                        bin_status=bin_status,
                    )
                    ok = send_to_thingspeak(settings.thingspeak_api_key, ts_payload)
                    print(f"ThingSpeak update: {'ok' if ok else 'failed'} | {ts_payload}")
            except Exception as exc:
                print(f"Error posting sensor value: {exc}")


if __name__ == "__main__":
    main()
