from pathlib import Path
from typing import Final

import numpy as np
from PIL import Image
from tensorflow.keras import Sequential
from tensorflow.keras.layers import Conv2D, Dense, Flatten, MaxPool2D
from tensorflow.keras.models import load_model

from app.core.config import settings

CLASS_NAMES: Final[list[str]] = ["plastic", "metal", "organic"]
IMAGE_SIZE: Final[tuple[int, int]] = (128, 128)


class WasteClassifier:
    def __init__(self, model_path: str):
        self.model_path = Path(model_path)
        self.model = None

    def load(self) -> None:
        if self.model_path.exists():
            self.model = load_model(self.model_path)
            return

        # Fallback model keeps API available when no trained file exists.
        self.model = Sequential(
            [
                Conv2D(16, (3, 3), activation="relu", input_shape=(128, 128, 3)),
                MaxPool2D(2, 2),
                Conv2D(32, (3, 3), activation="relu"),
                MaxPool2D(2, 2),
                Flatten(),
                Dense(64, activation="relu"),
                Dense(len(CLASS_NAMES), activation="softmax"),
            ]
        )
        self.model.compile(optimizer="adam", loss="categorical_crossentropy", metrics=["accuracy"])

    def predict_image(self, file_path: str) -> tuple[str, float]:
        if self.model is None:
            raise RuntimeError("Model not loaded")

        img = Image.open(file_path).convert("RGB").resize(IMAGE_SIZE)
        arr = np.array(img, dtype=np.float32) / 255.0
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
