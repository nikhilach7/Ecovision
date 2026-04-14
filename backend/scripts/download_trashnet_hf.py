from __future__ import annotations

from pathlib import Path
from typing import Any

from datasets import load_dataset

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "trashnet_raw"
HF_DATASET_ID = "garythung/trashnet"
TARGET_PER_CLASS = 200
TARGET_CLASSES = {
    "plastic": "plastic",
    "metal": "metal",
    "paper": "organic",
    "cardboard": "organic",
    "trash": "organic",
}
TRASHNET_LABELS = ["glass", "paper", "cardboard", "plastic", "metal", "trash"]


def pick_split(dataset_obj: Any):
    if hasattr(dataset_obj, "keys"):
        for split_name in ("train", "test", "validation", "default"):
            if split_name in dataset_obj:
                return dataset_obj[split_name]
        return next(iter(dataset_obj.values()))
    return dataset_obj


def main() -> None:
    print(f"Downloading dataset from Hugging Face: {HF_DATASET_ID}")
    dataset = load_dataset(HF_DATASET_ID, streaming=True)
    split = pick_split(dataset)
    label_names = TRASHNET_LABELS

    RAW_DIR.mkdir(parents=True, exist_ok=True)

    counts: dict[str, int] = {key: 0 for key in set(TARGET_CLASSES.values())}

    for index, sample in enumerate(split):
        if counts["plastic"] >= TARGET_PER_CLASS and counts["metal"] >= TARGET_PER_CLASS and counts["organic"] >= TARGET_PER_CLASS:
            break

        image_column = sample.get("image")
        label_value = sample.get("label")
        if image_column is None or label_value is None:
            continue

        if label_names is not None:
            if isinstance(label_value, int):
                label_name = str(label_names[int(label_value)]).lower()
            else:
                label_name = str(label_value).lower()
        else:
            label_name = str(label_value).lower()

        if label_name not in TARGET_CLASSES:
            continue

        target_class = TARGET_CLASSES[label_name]
        if counts[target_class] >= TARGET_PER_CLASS:
            continue

        target_dir = RAW_DIR / target_class
        target_dir.mkdir(parents=True, exist_ok=True)

        image = image_column
        image_path = target_dir / f"{target_class}_{index:05d}.jpg"
        image.save(image_path)
        counts[target_class] += 1

    total = sum(counts.values())
    if total == 0:
        raise RuntimeError("No TrashNet samples were saved. Check dataset labels and columns.")

    print(f"Saved {total} images to {RAW_DIR}")
    for class_name, count in sorted(counts.items()):
        print(f"  {class_name}: {count}")
    print("Next run: python scripts/prepare_trashnet_dataset.py")


if __name__ == "__main__":
    main()
