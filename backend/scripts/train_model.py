from pathlib import Path

import tensorflow as tf
from tensorflow.keras import layers
from tensorflow.keras.models import Sequential

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data" / "sample_dataset"
MODEL_DIR = ROOT / "model"
MODEL_PATH = MODEL_DIR / "waste_classifier.keras"
IMG_SIZE = (128, 128)
BATCH_SIZE = 16
EPOCHS = 7


def build_model() -> Sequential:
    return Sequential(
        [
            layers.Input(shape=(128, 128, 3)),
            layers.Rescaling(1.0 / 255),
            layers.Conv2D(16, 3, activation="relu"),
            layers.MaxPooling2D(),
            layers.Conv2D(32, 3, activation="relu"),
            layers.MaxPooling2D(),
            layers.Conv2D(64, 3, activation="relu"),
            layers.GlobalAveragePooling2D(),
            layers.Dense(64, activation="relu"),
            layers.Dense(3, activation="softmax"),
        ]
    )


def main() -> None:
    if not DATA_DIR.exists():
        raise FileNotFoundError(f"Dataset not found: {DATA_DIR}")

    train_ds = tf.keras.utils.image_dataset_from_directory(
        DATA_DIR,
        labels="inferred",
        label_mode="categorical",
        image_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        validation_split=0.2,
        subset="training",
        seed=42,
    )

    val_ds = tf.keras.utils.image_dataset_from_directory(
        DATA_DIR,
        labels="inferred",
        label_mode="categorical",
        image_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        validation_split=0.2,
        subset="validation",
        seed=42,
    )

    model = build_model()
    model.compile(optimizer="adam", loss="categorical_crossentropy", metrics=["accuracy"])

    model.fit(train_ds.prefetch(tf.data.AUTOTUNE), validation_data=val_ds.prefetch(tf.data.AUTOTUNE), epochs=EPOCHS)

    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    model.save(MODEL_PATH)
    print(f"Model saved to: {MODEL_PATH}")


if __name__ == "__main__":
    main()
