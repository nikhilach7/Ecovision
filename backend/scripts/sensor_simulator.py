import random
import time

import requests

from app.core.config import settings
from app.services.thingspeak import build_thingspeak_payload, send_to_thingspeak

API_URL = "http://localhost:8000/api/sensor"
BIN_ID = "BIN-01"
LOCATION = "Campus Block A"
MAX_DEPTH_CM = 40


def compute_metrics(distance_cm: float) -> tuple[float, float, int]:
    fill_level = round(max(0.0, min(100.0, (1 - (distance_cm / MAX_DEPTH_CM)) * 100)), 2)
    waste_level = round(100.0 - fill_level, 2)
    bin_status = 1 if fill_level > 90 else 0
    return fill_level, waste_level, bin_status


def main() -> None:
    print("Starting EcoVision sensor simulator...")
    while True:
        distance_cm = round(random.uniform(2, 38), 2)
        fill_level, waste_level, bin_status = compute_metrics(distance_cm)
        payload = {
            "bin_id": BIN_ID,
            "distance_cm": distance_cm,
            "max_depth_cm": MAX_DEPTH_CM,
            "location": LOCATION,
        }
        try:
            response = requests.post(API_URL, json=payload, timeout=5)
            print(f"Sent distance={distance_cm}cm -> {response.status_code}")
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
            print(f"Error sending reading: {exc}")
        time.sleep(5)


if __name__ == "__main__":
    main()
