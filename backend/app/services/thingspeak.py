from __future__ import annotations

import threading
import time

import requests

THINGSPEAK_BASE_URL = "https://api.thingspeak.com/update.json"
_last_sent_at_by_api_key: dict[str, float] = {}
_send_lock = threading.Lock()


def build_thingspeak_payload(*, fill_level: float, waste_level: float, distance_cm: float, bin_status: int) -> dict[str, str]:
    return {
        "field1": f"{fill_level:.2f}",
        "field2": f"{waste_level:.2f}",
        "field3": f"{distance_cm:.2f}",
        "field4": str(bin_status),
    }


def should_send_to_thingspeak(api_key: str, min_interval_seconds: int) -> bool:
    if min_interval_seconds <= 0:
        return True

    now = time.monotonic()
    key = api_key.strip()
    with _send_lock:
        last_sent = _last_sent_at_by_api_key.get(key)
        if last_sent is not None and (now - last_sent) < min_interval_seconds:
            return False
        _last_sent_at_by_api_key[key] = now
        return True


def send_to_thingspeak(api_key: str, payload: dict[str, str], timeout: int = 10) -> bool:
    response = requests.post(
        THINGSPEAK_BASE_URL,
        params={"api_key": api_key, **payload},
        timeout=timeout,
    )
    return response.ok
