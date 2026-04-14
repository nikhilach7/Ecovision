from __future__ import annotations

import requests

THINGSPEAK_BASE_URL = "https://api.thingspeak.com/update.json"


def build_thingspeak_payload(*, fill_level: float, waste_level: float, distance_cm: float, bin_status: int) -> dict[str, str]:
    return {
        "field1": f"{fill_level:.2f}",
        "field2": f"{waste_level:.2f}",
        "field3": f"{distance_cm:.2f}",
        "field4": str(bin_status),
    }


def send_to_thingspeak(api_key: str, payload: dict[str, str], timeout: int = 10) -> bool:
    response = requests.post(
        THINGSPEAK_BASE_URL,
        params={"api_key": api_key, **payload},
        timeout=timeout,
    )
    return response.ok
