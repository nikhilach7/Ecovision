import json
from pathlib import Path
from typing import Final

import numpy as np
from PIL import Image
from tensorflow.keras.applications.mobilenet_v2 import MobileNetV2, decode_predictions, preprocess_input
from tensorflow.keras.models import load_model

CLASS_NAMES: Final[list[str]] = ["plastic", "metal", "organic"]
DEFAULT_IMAGE_LABELS: Final[list[str]] = ["glass", "paper", "cardboard", "plastic", "metal", "trash"]
MODEL_METADATA_SUFFIX: Final[str] = ".json"


class WasteClassifier:
    def __init__(self, model_path: str):
        self.model_path = Path(model_path)
        self.metadata_path = self.model_path.with_suffix(MODEL_METADATA_SUFFIX)
        self.model = None
        self.mode = "custom"
        self.class_names: list[str] = []
        self.bin_mapping: dict[str, str] = {}

    def load(self) -> None:
        if self.model_path.exists():
            self.model = load_model(self.model_path)
            self.mode = "custom"
            self._load_metadata()
            return

        # If no project-trained model exists, use ImageNet-pretrained MobileNetV2.
        self.model = MobileNetV2(weights="imagenet")
        self.mode = "imagenet"
        self.class_names = list(DEFAULT_IMAGE_LABELS)
        self.bin_mapping = {label: self._map_imagenet_label_to_waste(label) for label in self.class_names}

    def _load_metadata(self) -> None:
        if not self.metadata_path.exists():
            self.class_names = list(CLASS_NAMES)
            self.bin_mapping = {label: label for label in self.class_names}
            return

        metadata = json.loads(self.metadata_path.read_text(encoding="utf-8"))
        self.class_names = [str(item) for item in metadata.get("class_names", [])]
        self.bin_mapping = {
            str(label): str(bin_label)
            for label, bin_label in metadata.get("bin_mapping", {}).items()
        }
        if not self.class_names:
            self.class_names = list(CLASS_NAMES)
        if not self.bin_mapping:
            self.bin_mapping = {label: label for label in self.class_names}

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

    def _predict_trained_model(self, file_path: str) -> tuple[str, str, float]:
        if self.model is None:
            raise RuntimeError("Model not loaded")

        img = Image.open(file_path).convert("RGB")
        arr = np.array(img.resize((224, 224)), dtype=np.float32)
        arr = np.expand_dims(arr, axis=0)
        arr = preprocess_input(arr)

        probs = self.model.predict(arr, verbose=0)[0]
        top_idx = int(np.argmax(probs))
        confidence = float(probs[top_idx])
        predicted_label = self.class_names[top_idx] if top_idx < len(self.class_names) else CLASS_NAMES[top_idx % len(CLASS_NAMES)]
        waste_type = self.bin_mapping.get(predicted_label, predicted_label)
        return predicted_label, waste_type, confidence

    def predict_image(self, file_path: str) -> tuple[str, str, float]:
        if self.model is None:
            raise RuntimeError("Model not loaded")

        if self.mode == "imagenet":
            img = Image.open(file_path).convert("RGB")
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
                    return "unknown", mapped, float(conf)
            return "unknown", "organic", 0.51

        return self._predict_trained_model(file_path)


classifier = WasteClassifier(settings.model_path)
