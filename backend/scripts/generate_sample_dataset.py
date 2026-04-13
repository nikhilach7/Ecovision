from pathlib import Path
import random

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "sample_dataset"
CLASSES = ["plastic", "metal", "organic"]
SIZE = (128, 128)
IMAGES_PER_CLASS = 120


def make_plastic() -> Image.Image:
    img = Image.new("RGB", SIZE, (18, 44, 88))
    d = ImageDraw.Draw(img)
    for _ in range(4):
        x1 = random.randint(15, 90)
        y1 = random.randint(10, 80)
        x2 = x1 + random.randint(15, 30)
        y2 = y1 + random.randint(35, 55)
        d.rounded_rectangle((x1, y1, x2, y2), radius=8, fill=(65, 140, 255))
    return img


def make_metal() -> Image.Image:
    img = Image.new("RGB", SIZE, (80, 80, 86))
    d = ImageDraw.Draw(img)
    for _ in range(5):
        x = random.randint(15, 100)
        y = random.randint(15, 100)
        r = random.randint(10, 18)
        d.ellipse((x - r, y - r, x + r, y + r), fill=(170, 170, 180), outline=(215, 215, 220), width=2)
    return img


def make_organic() -> Image.Image:
    img = Image.new("RGB", SIZE, (40, 78, 34))
    d = ImageDraw.Draw(img)
    for _ in range(6):
        x = random.randint(10, 95)
        y = random.randint(10, 95)
        w = random.randint(20, 35)
        h = random.randint(10, 24)
        d.ellipse((x, y, x + w, y + h), fill=(110, 78, 28))
    return img


def main() -> None:
    generators = {
        "plastic": make_plastic,
        "metal": make_metal,
        "organic": make_organic,
    }

    for cls in CLASSES:
        cls_dir = OUT / cls
        cls_dir.mkdir(parents=True, exist_ok=True)
        for idx in range(IMAGES_PER_CLASS):
            img = generators[cls]()
            img.save(cls_dir / f"{cls}_{idx:03d}.png")

    print(f"Dataset generated at: {OUT}")


if __name__ == "__main__":
    main()
