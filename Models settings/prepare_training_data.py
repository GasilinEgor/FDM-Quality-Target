"""
Собирает из папок data/<класс> и labels/<режим>/<класс> структуру YOLO
(images/train|val, labels/train|val) и датасет классификации defect_classification.
"""
from __future__ import annotations

import random
import shutil
from pathlib import Path

CLASSES = [
    "Cracking",
    "Layer_shifting",
    "Off_platform",
    "Stringing",
    "Warping",
]

DATASET_ROOT = Path("datasets") / "FDM-3D-Printing-Defect-Dataset"
DATA_DIR = DATASET_ROOT / "data"
LABELS_ROOT = DATASET_ROOT / "labels"
PREPARED = DATASET_ROOT / "prepared"
CLS_ROOT = DATASET_ROOT / "defect_classification"

IMG_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def _collect_pairs(label_mode: str) -> list[tuple[Path, Path, str]]:
    pairs: list[tuple[Path, Path, str]] = []
    label_base = LABELS_ROOT / label_mode
    for cls in CLASSES:
        img_dir = DATA_DIR / cls
        lbl_dir = label_base / cls
        if not img_dir.is_dir() or not lbl_dir.is_dir():
            continue
        for img_path in sorted(img_dir.iterdir()):
            if img_path.suffix.lower() not in IMG_EXTS:
                continue
            lbl_path = lbl_dir / f"{img_path.stem}.txt"
            if not lbl_path.is_file():
                continue
            unique = f"{cls}_{img_path.stem}{img_path.suffix.lower()}"
            pairs.append((img_path, lbl_path, unique))
    return pairs


def _write_yolo_yaml(out_dir: Path, nc: int, names: list[str]) -> None:
    lines = [
        f"path: {out_dir.as_posix()}",
        "train: images/train",
        "val: images/val",
        "",
        f"nc: {nc}",
        "names:",
    ]
    for i, n in enumerate(names):
        lines.append(f"  {i}: {n}")
    (out_dir / "data.yaml").write_text("\n".join(lines) + "\n", encoding="utf-8")


def prepare_detection_split(label_mode: str, yaml_names: list[str]) -> Path:
    out_dir = PREPARED / label_mode
    for sub in ("images/train", "images/val", "labels/train", "labels/val"):
        p = out_dir / sub
        p.mkdir(parents=True, exist_ok=True)
        for f in p.iterdir():
            if f.is_file():
                f.unlink()

    pairs = _collect_pairs(label_mode)
    if not pairs:
        raise RuntimeError(f"Нет пар изображение+разметка для режима {label_mode}")

    rng = random.Random(42)
    rng.shuffle(pairs)
    n_train = max(1, int(0.8 * len(pairs)))
    train_pairs = pairs[:n_train]
    val_pairs = pairs[n_train:] or pairs[:1]

    def copy_split(items: list[tuple[Path, Path, str]], split: str) -> None:
        for img_path, lbl_path, unique in items:
            shutil.copy2(img_path, out_dir / "images" / split / unique)
            dest_lbl = out_dir / "labels" / split / Path(unique).with_suffix(".txt").name
            shutil.copy2(lbl_path, dest_lbl)

    copy_split(train_pairs, "train")
    copy_split(val_pairs, "val")

    _write_yolo_yaml(out_dir, len(yaml_names), yaml_names)
    return out_dir


def prepare_classification_split() -> Path:
    for split in ("train", "val"):
        for cls in CLASSES:
            p = CLS_ROOT / split / cls
            p.mkdir(parents=True, exist_ok=True)
            for f in p.rglob("*"):
                if f.is_file():
                    f.unlink()

    rng = random.Random(42)
    for cls in CLASSES:
        img_dir = DATA_DIR / cls
        if not img_dir.is_dir():
            continue
        imgs = sorted(
            p
            for p in img_dir.iterdir()
            if p.suffix.lower() in IMG_EXTS
        )
        rng.shuffle(imgs)
        n_train = max(1, int(0.8 * len(imgs)))
        train_imgs = imgs[:n_train]
        val_imgs = imgs[n_train:] or imgs[:1]
        for p in train_imgs:
            shutil.copy2(p, CLS_ROOT / "train" / cls / p.name)
        for p in val_imgs:
            shutil.copy2(p, CLS_ROOT / "val" / cls / p.name)

    return CLS_ROOT


def main() -> None:
    PREPARED.mkdir(parents=True, exist_ok=True)
    mp = prepare_detection_split(
        "model_presence",
        ["3D_model", "No_3D_model"],
    )
    dt = prepare_detection_split(
        "defect_type",
        CLASSES.copy(),
    )
    cls_dir = prepare_classification_split()
    print(f"model_presence: {mp / 'data.yaml'}")
    print(f"defect_type: {dt / 'data.yaml'}")
    print(f"classification: {cls_dir}")


if __name__ == "__main__":
    main()
