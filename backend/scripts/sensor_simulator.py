import random
import time

import requests

API_URL = "http://localhost:8000/api/sensor"
BIN_ID = "BIN-01"
LOCATION = "Campus Block A"


def main() -> None:
    print("Starting EcoVision sensor simulator...")
    while True:
        distance_cm = round(random.uniform(2, 38), 2)
        payload = {
            "bin_id": BIN_ID,
            "distance_cm": distance_cm,
            "max_depth_cm": 40,
            "location": LOCATION,
        }
        try:
            response = requests.post(API_URL, json=payload, timeout=5)
            print(f"Sent distance={distance_cm}cm -> {response.status_code}")
        except Exception as exc:
            print(f"Error sending reading: {exc}")
        time.sleep(5)


if __name__ == "__main__":
    main()
