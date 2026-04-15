from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from PIL import Image
import tensorflow as tf
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input

ROOT = Path(__file__).resolve().parents[1]
TFLITE_PATH = ROOT / "model" / "waste_classifier.tflite"
METADATA_PATH = ROOT / "model" / "waste_classifier.json"


def load_metadata() -> tuple[list[str], dict[str, str]]:
    metadata = json.loads(METADATA_PATH.read_text(encoding="utf-8"))
    class_names = [str(item) for item in metadata.get("class_names", [])]
    bin_mapping = {
        str(key): str(value)
        for key, value in metadata.get("bin_mapping", {}).items()
    }
    if not class_names:
        raise RuntimeError("No class_names found in model metadata.")
    return class_names, bin_mapping


def prepare_input(image_path: Path, image_size: tuple[int, int]) -> np.ndarray:
    image = Image.open(image_path).convert("RGB")
    array = np.array(image.resize(image_size), dtype=np.float32)
    array = np.expand_dims(array, axis=0)
    return array


def main() -> None:
    parser = argparse.ArgumentParser(description="Run local TFLite prediction on one image.")
    parser.add_argument("image", type=Path, help="Path to image file")
    args = parser.parse_args()

    if not args.image.exists():
        raise FileNotFoundError(f"Image not found: {args.image}")
    if not TFLITE_PATH.exists():
        raise FileNotFoundError(f"TFLite model not found at {TFLITE_PATH}. Run training first.")
    if not METADATA_PATH.exists():
        raise FileNotFoundError(f"Metadata not found at {METADATA_PATH}. Run training first.")

    class_names, bin_mapping = load_metadata()

    interpreter = tf.lite.Interpreter(model_path=str(TFLITE_PATH))
    interpreter.allocate_tensors()
    input_details = interpreter.get_input_details()[0]
    output_details = interpreter.get_output_details()[0]

    # MobileNetV2 models here are fixed to 224x224 RGB.
    batch = prepare_input(args.image, (224, 224)).astype(np.float32)
    interpreter.set_tensor(input_details["index"], batch)
    interpreter.invoke()

    probs = interpreter.get_tensor(output_details["index"])[0]
    top_index = int(np.argmax(probs))
    confidence = float(probs[top_index])
    predicted_label = class_names[top_index]
    waste_type = bin_mapping.get(predicted_label, predicted_label)

    print(f"image={args.image}")
    print(f"predicted_label={predicted_label}")
    print(f"waste_type={waste_type}")
    print(f"confidence={confidence:.4f}")


if __name__ == "__main__":
    main()
