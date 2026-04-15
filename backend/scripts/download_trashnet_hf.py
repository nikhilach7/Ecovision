from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any

from datasets import load_dataset

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "trashnet_raw"
HF_DATASET_ID = "garythung/trashnet"
TARGET_PER_CLASS = 200
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

    RAW_DIR.mkdir(parents=True, exist_ok=True)

    counts: Counter[str] = Counter({label: 0 for label in TRASHNET_LABELS})

    for index, sample in enumerate(split):
        if all(counts[label] >= TARGET_PER_CLASS for label in TRASHNET_LABELS):
            break

        image_column = sample.get("image")
        label_value = sample.get("label")
        if image_column is None or label_value is None:
            continue

        if isinstance(label_value, int):
            label_name = str(TRASHNET_LABELS[int(label_value)]).lower()
        else:
            label_name = str(label_value).lower()

        if label_name not in TRASHNET_LABELS:
            continue

        if counts[label_name] >= TARGET_PER_CLASS:
            continue

        target_dir = RAW_DIR / label_name
        target_dir.mkdir(parents=True, exist_ok=True)

        image = image_column
        image_path = target_dir / f"{label_name}_{index:05d}.jpg"
        image.save(image_path)
        counts[label_name] += 1

    total = sum(counts.values())
    if total == 0:
        raise RuntimeError("No TrashNet samples were saved. Check dataset labels and columns.")

    print(f"Saved {total} images to {RAW_DIR}")
    for class_name, count in sorted(counts.items()):
        print(f"  {class_name}: {count}")
    print("Next run: python scripts/prepare_trashnet_dataset.py")


if __name__ == "__main__":
    main()
