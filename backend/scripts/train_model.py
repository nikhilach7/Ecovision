import json
import random
from collections import Counter
from pathlib import Path

import numpy as np
import tensorflow as tf
from tensorflow.keras import layers
from tensorflow.keras.applications.mobilenet_v2 import MobileNetV2, preprocess_input
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
from tensorflow.keras.models import Model

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA_DIR = ROOT / "data"
TRASHNET_COMPACT_DIR = ROOT / "data" / "trashnet_compact"
TRASHNET_RAW_DIR = ROOT / "data" / "trashnet_raw"
SAMPLE_DATA_DIR = ROOT / "data" / "sample_dataset"
MODEL_DIR = ROOT / "model"
MODEL_PATH = MODEL_DIR / "waste_classifier.keras"
METADATA_PATH = MODEL_DIR / "waste_classifier.json"
SAVED_MODEL_DIR = MODEL_DIR / "saved_model"
TFLITE_PATH = MODEL_DIR / "waste_classifier.tflite"
TRAINING_REPORT_PATH = MODEL_DIR / "training_report.json"
IMG_SIZE = (224, 224)
BATCH_SIZE = 16
HEAD_EPOCHS = 15
FINE_TUNE_EPOCHS = 10
VALIDATION_SPLIT = 0.2
SEED = 42
CLASS_TO_BIN = {
    "glass": "organic",
    "paper": "organic",
    "cardboard": "organic",
    "trash": "organic",
    "plastic": "plastic",
    "metal": "metal",
    "organic": "organic",
}


def _has_image_files(folder: Path) -> bool:
    return any(
        item.is_file() and item.suffix.lower() in {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
        for item in folder.iterdir()
    )


def discover_dataset_dir() -> Path:
    # If user pasted class folders directly under backend/data, prefer that.
    if DEFAULT_DATA_DIR.exists():
        direct_classes = [
            item
            for item in DEFAULT_DATA_DIR.iterdir()
            if item.is_dir() and not item.name.startswith(".") and _has_image_files(item)
        ]
        if len(direct_classes) >= 2:
            return DEFAULT_DATA_DIR
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
        kwargs.update(validation_split=VALIDATION_SPLIT, subset=subset)
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


def evaluate_per_class(model: Model, val_ds: tf.data.Dataset, class_names: list[str]) -> dict[str, object]:
    y_true: list[int] = []
    y_pred: list[int] = []

    for images, labels in val_ds:
        probs = model.predict(images, verbose=0)
        y_pred.extend(np.argmax(probs, axis=1).tolist())
        y_true.extend(np.argmax(labels.numpy(), axis=1).tolist())

    if not y_true:
        return {
            "overall_accuracy": 0.0,
            "macro_precision": 0.0,
            "macro_recall": 0.0,
            "macro_f1": 0.0,
            "confusion_matrix": [],
            "per_class": {},
        }

    cm = tf.math.confusion_matrix(y_true, y_pred, num_classes=len(class_names)).numpy()
    per_class: dict[str, dict[str, float]] = {}
    precisions: list[float] = []
    recalls: list[float] = []
    f1_scores: list[float] = []

    for index, name in enumerate(class_names):
        tp = float(cm[index, index])
        fp = float(cm[:, index].sum() - tp)
        fn = float(cm[index, :].sum() - tp)
        support = float(cm[index, :].sum())

        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0
        class_accuracy = tp / support if support > 0 else 0.0

        per_class[name] = {
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1": round(f1, 4),
            "accuracy": round(class_accuracy, 4),
            "support": int(support),
        }
        precisions.append(precision)
        recalls.append(recall)
        f1_scores.append(f1)

    overall_accuracy = float((cm.diagonal().sum()) / cm.sum()) if cm.sum() else 0.0
    report = {
        "overall_accuracy": round(overall_accuracy, 4),
        "macro_precision": round(float(np.mean(precisions)), 4),
        "macro_recall": round(float(np.mean(recalls)), 4),
        "macro_f1": round(float(np.mean(f1_scores)), 4),
        "confusion_matrix": cm.astype(int).tolist(),
        "per_class": per_class,
    }
    return report


def export_tflite(model: Model) -> None:
    converter = tf.lite.TFLiteConverter.from_keras_model(model)
    converter.optimizations = [tf.lite.Optimize.DEFAULT]
    converter.target_spec.supported_types = [tf.float16]
    tflite_model = converter.convert()
    TFLITE_PATH.write_bytes(tflite_model)


def save_metadata(class_names: list[str]) -> None:
    metadata = {
        "class_names": class_names,
        "bin_mapping": {class_name: CLASS_TO_BIN.get(class_name, class_name) for class_name in class_names},
        "image_size": list(IMG_SIZE),
        "model_artifacts": {
            "keras": MODEL_PATH.name,
            "saved_model": SAVED_MODEL_DIR.name,
            "tflite": TFLITE_PATH.name,
        },
        "preprocessing": "mobilenet_v2_preprocess_input",
        "seed": SEED,
    }
    METADATA_PATH.write_text(json.dumps(metadata, indent=2), encoding="utf-8")


def main() -> None:
    random.seed(SEED)
    np.random.seed(SEED)
    tf.random.set_seed(SEED)

    data_dir = discover_dataset_dir()
    class_names = infer_class_names(data_dir)

    print(f"Training from dataset: {data_dir}")
    print(f"Detected classes: {', '.join(class_names)}")

    # Unshuffled dataset is used for stable class-weight computation.
    train_for_weights = make_dataset(data_dir, subset="training", seed=SEED)
    class_weight = compute_class_weights(train_for_weights, class_names)

    train_ds = make_dataset(data_dir, subset="training", seed=SEED)
    val_ds = make_dataset(data_dir, subset="validation", seed=SEED)

    autotune = tf.data.AUTOTUNE
    train_ds = train_ds.cache().shuffle(1000).prefetch(buffer_size=autotune)
    val_ds = val_ds.cache().prefetch(buffer_size=autotune)

    model, base_model = build_model(len(class_names))
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=1e-3),
        loss="categorical_crossentropy",
        metrics=["accuracy"],
    )

    callbacks = [
        EarlyStopping(monitor="val_accuracy", patience=4, restore_best_weights=True),
        ReduceLROnPlateau(monitor="val_loss", factor=0.2, patience=2, min_lr=1e-6),
    ]

    head_history = model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=HEAD_EPOCHS,
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

        fine_tune_history = model.fit(
            train_ds,
            validation_data=val_ds,
            epochs=FINE_TUNE_EPOCHS,
            class_weight=class_weight or None,
            callbacks=callbacks,
            verbose=1,
        )
    else:
        fine_tune_history = None

    eval_loss, eval_accuracy = model.evaluate(val_ds, verbose=0)
    metrics_report = evaluate_per_class(model, val_ds, class_names)

    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    model.save(MODEL_PATH)
    model.export(str(SAVED_MODEL_DIR))
    export_tflite(model)
    save_metadata(class_names)

    training_report = {
        "dataset": str(data_dir),
        "class_names": class_names,
        "class_weight": {str(k): round(v, 4) for k, v in class_weight.items()},
        "validation": {
            "loss": round(float(eval_loss), 4),
            "accuracy": round(float(eval_accuracy), 4),
        },
        "metrics": metrics_report,
        "history": {
            "head": {key: [float(v) for v in values] for key, values in head_history.history.items()},
            "fine_tune": (
                {key: [float(v) for v in values] for key, values in fine_tune_history.history.items()}
                if fine_tune_history is not None
                else {}
            ),
        },
    }
    TRAINING_REPORT_PATH.write_text(json.dumps(training_report, indent=2), encoding="utf-8")

    print(f"Model saved to: {MODEL_PATH}")
    print(f"SavedModel exported to: {SAVED_MODEL_DIR}")
    print(f"TFLite model exported to: {TFLITE_PATH}")
    print(f"Metadata saved to: {METADATA_PATH}")
    print(f"Training report saved to: {TRAINING_REPORT_PATH}")
    print(
        "Validation summary -> "
        f"accuracy={training_report['validation']['accuracy']:.4f}, "
        f"macro_f1={training_report['metrics']['macro_f1']:.4f}"
    )


if __name__ == "__main__":
    main()
