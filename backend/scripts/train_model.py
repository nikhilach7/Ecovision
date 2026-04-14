import json
from collections import Counter
from pathlib import Path

import tensorflow as tf
from tensorflow.keras import layers
from tensorflow.keras.applications.mobilenet_v2 import MobileNetV2, preprocess_input
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
from tensorflow.keras.models import Model

ROOT = Path(__file__).resolve().parents[1]
TRASHNET_COMPACT_DIR = ROOT / "data" / "trashnet_compact"
TRASHNET_RAW_DIR = ROOT / "data" / "trashnet_raw"
SAMPLE_DATA_DIR = ROOT / "data" / "sample_dataset"
MODEL_DIR = ROOT / "model"
MODEL_PATH = MODEL_DIR / "waste_classifier.keras"
METADATA_PATH = MODEL_DIR / "waste_classifier.json"
IMG_SIZE = (224, 224)
BATCH_SIZE = 16
EPOCHS = 12
FINE_TUNE_EPOCHS = 4
CLASS_TO_BIN = {
    "glass": "organic",
    "paper": "organic",
    "cardboard": "organic",
    "trash": "organic",
    "plastic": "plastic",
    "metal": "metal",
    "organic": "organic",
}


def discover_dataset_dir() -> Path:
    if TRASHNET_COMPACT_DIR.exists():
        return TRASHNET_COMPACT_DIR
    if TRASHNET_RAW_DIR.exists():
        return TRASHNET_RAW_DIR
    if SAMPLE_DATA_DIR.exists():
        return SAMPLE_DATA_DIR
    raise FileNotFoundError(
        f"Dataset not found: {TRASHNET_COMPACT_DIR}, {TRASHNET_RAW_DIR} or {SAMPLE_DATA_DIR}"
    )


def infer_class_names(data_dir: Path) -> list[str]:
    class_names = sorted([item.name for item in data_dir.iterdir() if item.is_dir()])
    if not class_names:
        raise RuntimeError(f"No class folders found in {data_dir}")
    return class_names


def make_dataset(data_dir: Path, subset: str | None, seed: int = 42):
    kwargs = dict(
        labels="inferred",
        label_mode="categorical",
        image_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        seed=seed,
    )
    if subset is not None:
        kwargs.update(validation_split=0.2, subset=subset)
    return tf.keras.utils.image_dataset_from_directory(data_dir, **kwargs)


def compute_class_weights(train_ds: tf.data.Dataset, class_names: list[str]) -> dict[int, float]:
    counts = Counter()
    for _images, labels in train_ds:
        label_indices = tf.argmax(labels, axis=1).numpy().tolist()
        counts.update(label_indices)

    total = sum(counts.values())
    if total == 0:
        return {}

    class_weight: dict[int, float] = {}
    class_count = len(class_names)
    for index in range(class_count):
        count = counts.get(index, 0)
        if count:
            class_weight[index] = total / (class_count * count)
    return class_weight


def build_model(num_classes: int) -> tuple[Model, Model]:
    data_augmentation = tf.keras.Sequential(
        [
            layers.RandomFlip("horizontal"),
            layers.RandomRotation(0.08),
            layers.RandomZoom(0.1),
            layers.RandomContrast(0.1),
        ],
        name="augmentation",
    )

    inputs = layers.Input(shape=(*IMG_SIZE, 3))
    x = data_augmentation(inputs)
    x = layers.Lambda(preprocess_input, name="mobilenet_preprocess")(x)

    base_model = MobileNetV2(
        include_top=False,
        weights="imagenet",
        input_tensor=x,
        pooling="avg",
    )
    base_model.trainable = False

    x = layers.Dropout(0.25)(base_model.output)
    outputs = layers.Dense(num_classes, activation="softmax")(x)
    model = Model(inputs=inputs, outputs=outputs, name="waste_classifier_mobilenetv2")
    return model, base_model


def save_metadata(class_names: list[str]) -> None:
    metadata = {
        "class_names": class_names,
        "bin_mapping": {class_name: CLASS_TO_BIN.get(class_name, class_name) for class_name in class_names},
        "image_size": list(IMG_SIZE),
    }
    METADATA_PATH.write_text(json.dumps(metadata, indent=2), encoding="utf-8")


def main() -> None:
    data_dir = discover_dataset_dir()
    class_names = infer_class_names(data_dir)

    print(f"Training from dataset: {data_dir}")
    print(f"Detected classes: {', '.join(class_names)}")

    train_ds = make_dataset(data_dir, subset="training")
    val_ds = make_dataset(data_dir, subset="validation")

    autotune = tf.data.AUTOTUNE
    train_ds = train_ds.cache().shuffle(1000).prefetch(buffer_size=autotune)
    val_ds = val_ds.cache().prefetch(buffer_size=autotune)

    model, base_model = build_model(len(class_names))
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=1e-3),
        loss="categorical_crossentropy",
        metrics=["accuracy"],
    )

    class_weight = compute_class_weights(train_ds, class_names)

    callbacks = [
        EarlyStopping(monitor="val_accuracy", patience=3, restore_best_weights=True),
        ReduceLROnPlateau(monitor="val_loss", factor=0.2, patience=2, min_lr=1e-6),
    ]

    model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=EPOCHS,
        class_weight=class_weight or None,
        callbacks=callbacks,
        verbose=1,
    )

    if len(base_model.layers) > 20:
        base_model.trainable = True
        for layer in base_model.layers[:-20]:
            layer.trainable = False

        model.compile(
            optimizer=tf.keras.optimizers.Adam(learning_rate=1e-5),
            loss="categorical_crossentropy",
            metrics=["accuracy"],
        )

        model.fit(
            train_ds,
            validation_data=val_ds,
            epochs=FINE_TUNE_EPOCHS,
            class_weight=class_weight or None,
            callbacks=callbacks,
            verbose=1,
        )

    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    model.save(MODEL_PATH)
    save_metadata(class_names)
    print(f"Model saved to: {MODEL_PATH}")
    print(f"Metadata saved to: {METADATA_PATH}")


if __name__ == "__main__":
    main()
