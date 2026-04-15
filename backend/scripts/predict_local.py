from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from PIL import Image
import tensorflow as tf
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input

ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = ROOT / "model" / "waste_classifier.keras"
METADATA_PATH = ROOT / "model" / "waste_classifier.json"


def load_metadata() -> tuple[list[str], dict[str, str]]:
    if not METADATA_PATH.exists():
        raise FileNotFoundError(
            f"Model metadata not found at {METADATA_PATH}. Run training first."
        )

    metadata = json.loads(METADATA_PATH.read_text(encoding="utf-8"))
    class_names = [str(item) for item in metadata.get("class_names", [])]
    if not class_names:
        raise RuntimeError("No class_names found in model metadata.")
    bin_mapping = {
        str(key): str(value)
        for key, value in metadata.get("bin_mapping", {}).items()
    }
    return class_names, bin_mapping


def prepare_image(image_path: Path, image_size: tuple[int, int]) -> np.ndarray:
    image = Image.open(image_path).convert("RGB")
    array = np.array(image.resize(image_size), dtype=np.float32)
    array = np.expand_dims(array, axis=0)
    return array


def main() -> None:
    parser = argparse.ArgumentParser(description="Run local waste prediction on one image.")
    parser.add_argument("image", type=Path, help="Path to image file")
    args = parser.parse_args()

    if not args.image.exists():
        raise FileNotFoundError(f"Image not found: {args.image}")
    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"Trained model not found at {MODEL_PATH}. Run training first.")

    class_names, bin_mapping = load_metadata()
    model = tf.keras.models.load_model(
        MODEL_PATH,
        custom_objects={"preprocess_input": preprocess_input},
        compile=False,
    )

    batch = prepare_image(args.image, (224, 224))
    probabilities = model.predict(batch, verbose=0)[0]
    top_index = int(np.argmax(probabilities))

    predicted_label = class_names[top_index]
    confidence = float(probabilities[top_index])
    waste_type = bin_mapping.get(predicted_label, predicted_label)

    print(f"image={args.image}")
    print(f"predicted_label={predicted_label}")
    print(f"waste_type={waste_type}")
    print(f"confidence={confidence:.4f}")


if __name__ == "__main__":
    main()
