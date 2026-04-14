from pathlib import Path
from typing import Final

import numpy as np
from PIL import Image
from tensorflow.keras import Sequential
from tensorflow.keras.applications.mobilenet_v2 import MobileNetV2, decode_predictions, preprocess_input
from tensorflow.keras.layers import Conv2D, Dense, Flatten, MaxPool2D
from tensorflow.keras.models import load_model

from app.core.config import settings

CLASS_NAMES: Final[list[str]] = ["plastic", "metal", "organic"]
IMAGE_SIZE: Final[tuple[int, int]] = (128, 128)


class WasteClassifier:
    def __init__(self, model_path: str):
        self.model_path = Path(model_path)
        self.model = None
        self.mode = "custom"

    def load(self) -> None:
        if self.model_path.exists():
            self.model = load_model(self.model_path)
            self.mode = "custom"
            return

        # If no project-trained model exists, use ImageNet-pretrained MobileNetV2.
        self.model = MobileNetV2(weights="imagenet")
        self.mode = "imagenet"

    @staticmethod
    def _map_imagenet_label_to_waste(label: str) -> str:
        lower = label.lower()
        metal_keywords = {
            "can",
            "steel",
            "iron",
            "aluminum",
            "chain",
            "wrench",
            "nail",
            "bolt",
            "padlock",
            "knife",
            "spoon",
            "fork",
        }
        plastic_keywords = {
            "bottle",
            "packet",
            "container",
            "jug",
            "shampoo",
            "lotion",
            "water_bottle",
            "plastic",
        }

        if any(word in lower for word in metal_keywords):
            return "metal"
        if any(word in lower for word in plastic_keywords):
            return "plastic"
        return "organic"

    def predict_image(self, file_path: str) -> tuple[str, float]:
        if self.model is None:
            raise RuntimeError("Model not loaded")

        img = Image.open(file_path).convert("RGB")

        if self.mode == "imagenet":
            resized = img.resize((224, 224))
            arr = np.array(resized, dtype=np.float32)
            arr = np.expand_dims(arr, axis=0)
            arr = preprocess_input(arr)

            probs = self.model.predict(arr, verbose=0)
            decoded = decode_predictions(probs, top=5)[0]
            # decoded tuples are (class_id, label, confidence)
            for _, label, conf in decoded:
                mapped = self._map_imagenet_label_to_waste(label)
                if mapped in CLASS_NAMES:
                    return mapped, float(conf)
            return "organic", 0.51

        arr = np.array(img.resize(IMAGE_SIZE), dtype=np.float32) / 255.0
        arr = np.expand_dims(arr, axis=0)

        probs = self.model.predict(arr, verbose=0)[0]
        top_idx = int(np.argmax(probs))
        confidence = float(probs[top_idx])
        if confidence < settings.confidence_threshold:
            # Heuristic fallback to keep demo usable before proper training.
            rgb_mean = np.mean(arr[0], axis=(0, 1))
            if rgb_mean[2] > rgb_mean[1] and rgb_mean[2] > rgb_mean[0]:
                return "plastic", max(confidence, 0.56)
            if abs(rgb_mean[0] - rgb_mean[1]) < 0.06 and abs(rgb_mean[1] - rgb_mean[2]) < 0.06:
                return "metal", max(confidence, 0.58)
            return "organic", max(confidence, 0.55)

        return CLASS_NAMES[top_idx], confidence


classifier = WasteClassifier(settings.model_path)
