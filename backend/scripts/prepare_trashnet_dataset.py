from __future__ import annotations

from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "trashnet_raw"
OUT_DIR = ROOT / "data" / "trashnet_compact"
TARGET_CLASSES = {
    "plastic": ["plastic"],
    "metal": ["metal"],
    "organic": ["paper", "cardboard", "trash"],
}
VALID_EXTENSIONS = {".jpg", ".jpeg", ".png"}


def copy_images(source_dir: Path, target_dir: Path) -> int:
    count = 0
    target_dir.mkdir(parents=True, exist_ok=True)
    for image_path in source_dir.iterdir():
        if image_path.is_file() and image_path.suffix.lower() in VALID_EXTENSIONS:
            destination = target_dir / image_path.name
            shutil.copy2(image_path, destination)
            count += 1
    return count


def main() -> None:
    if not RAW_DIR.exists():
        raise FileNotFoundError(
            f"TrashNet raw dataset folder not found: {RAW_DIR}. "
            "Place the downloaded TrashNet-style dataset there first."
        )

    total_copied = 0
    for target_class, source_classes in TARGET_CLASSES.items():
        for source_class in source_classes:
            source_dir = RAW_DIR / source_class
            if not source_dir.exists():
                continue
            copied = copy_images(source_dir, OUT_DIR / target_class)
            total_copied += copied
            print(f"Copied {copied} images from {source_class} to {target_class}")

    if total_copied == 0:
        raise RuntimeError(
            f"No images were copied from {RAW_DIR}. Check the TrashNet folder structure."
        )

    print(f"Prepared compact dataset at: {OUT_DIR}")
    print("Class mapping: plastic -> plastic, metal -> metal, paper/cardboard/trash -> organic")


if __name__ == "__main__":
    main()
