from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path
from typing import Any

import cv2
import numpy as np
from ultralytics import YOLO


def _use_amp(device: str) -> bool:
    """На CPU смешанная точность часто падает на Windows — отключаем AMP."""
    return str(device).lower() != "cpu"


def _deterministic_for_device(device: str) -> bool:
    """
    deterministic=True на PyTorch 2.11 + Python 3.13 (CPU, Windows) даёт падение
    процесса (0xC0000005) при старте эпохи. На GPU обычно оставляют True.
    """
    return str(device).lower() != "cpu"


def _cpu_train_safety_kwargs(device: str) -> dict[str, Any]:
    """
    На CPU (Windows + Python 3.13) периодическая валидация в train() часто приводит к
    аварийному завершении процесса. Отключаем val/plots в train — итоговая проверка
    весов Ultralytics выполняет после эпох.
    """
    if str(device).lower() == "cpu":
        return {"val": False, "plots": False}
    return {}


def ensure_data_file(data_path: Path) -> None:
    if data_path.exists():
        return
    raise FileNotFoundError(
        f"Dataset config not found: {data_path}\n"
        "Create labels and data.yaml first, then rerun training."
    )


def ensure_classification_data(data_dir: Path) -> None:
    if not data_dir.is_dir():
        raise FileNotFoundError(
            f"Classification dataset folder not found: {data_dir}\n"
            "Expected structure: <root>/train/<class_name>/*.jpg and <root>/val/<class_name>/*.jpg"
        )
    for split in ("train", "val"):
        p = data_dir / split
        if not p.is_dir():
            raise FileNotFoundError(
                f"Missing '{split}' in classification dataset: {data_dir}"
            )


def train_yolov9_detection(
    data_yaml: str | Path,
    weights: str = "yolov9c.pt",
    epochs: int = 20,
    imgsz: int = 640,
    batch: int = 16,
    workers: int = 8,
    project: str = "runs/yolov9",
    name: str = "train",
    device: str = "0",
    patience: int = 30,
    freeze: int = 0,
    run_val: bool = True,
) -> dict[str, Any]:
    """
    Обучение модели детекции YOLOv9 (один датасет = один YAML с bbox-разметкой).
    """
    data_path = Path(data_yaml)
    ensure_data_file(data_path)

    model = YOLO(weights)
    train_results = model.train(
        data=str(data_path),
        epochs=epochs,
        imgsz=imgsz,
        batch=batch,
        workers=workers,
        project=project,
        name=name,
        device=device,
        patience=patience,
        freeze=freeze,
        pretrained=True,
        amp=_use_amp(device),
        deterministic=_deterministic_for_device(device),
        **_cpu_train_safety_kwargs(device),
    )

    save_dir = Path(train_results.save_dir)
    best_weights = save_dir / "weights" / "best.pt"
    val_metrics: dict[str, Any] | None = None

    if run_val and str(device).lower() != "cpu":
        val_results = model.val(
            data=str(data_path),
            split="val",
            imgsz=imgsz,
            batch=batch,
            device=device,
            amp=_use_amp(device),
        )
        val_metrics = val_results.results_dict

    return {
        "save_dir": save_dir,
        "best_weights": best_weights,
        "train_results": train_results,
        "val_metrics": val_metrics,
    }


def train_yolov9_defect_detection(
    data_yaml: str | Path | None = None,
    weights: str = "yolov9c.pt",
    project: str = "runs/yolov9",
    name: str = "defect_detection",
    **kwargs: Any,
) -> dict[str, Any]:
    """
    Обучение YOLOv9 для детекции дефектов (разметка типов дефектов в YOLO-детекции).
    По умолчанию: datasets/.../defect_type/data.yaml
    """
    if data_yaml is None:
        data_yaml = (
            Path("datasets")
            / "FDM-3D-Printing-Defect-Dataset"
            / "defect_type"
            / "data.yaml"
        )
    return train_yolov9_detection(
        data_yaml=data_yaml,
        weights=weights,
        project=project,
        name=name,
        **kwargs,
    )


def train_yolo11_defect_classification(
    data_dir: str | Path,
    model: str = "yolo11n-cls.pt",
    epochs: int = 20,
    imgsz: int = 224,
    batch: int = 32,
    workers: int = 8,
    project: str = "runs/yolo11_cls",
    name: str = "defect_classification",
    device: str = "0",
    patience: int = 30,
    run_val: bool = True,
) -> dict[str, Any]:
    """
    Обучение YOLO11 для классификации типа дефекта (task=classify).
    Структура данных: <data_dir>/train/<класс>/*, <data_dir>/val/<класс>/*
    """
    root = Path(data_dir)
    ensure_classification_data(root)

    m = YOLO(model)
    train_results = m.train(
        task="classify",
        data=str(root),
        epochs=epochs,
        imgsz=imgsz,
        batch=batch,
        workers=workers,
        project=project,
        name=name,
        device=device,
        patience=patience,
        pretrained=True,
        amp=_use_amp(device),
        deterministic=_deterministic_for_device(device),
        **_cpu_train_safety_kwargs(device),
    )

    save_dir = Path(train_results.save_dir)
    best_weights = save_dir / "weights" / "best.pt"
    val_metrics: dict[str, Any] | None = None

    if run_val and str(device).lower() != "cpu":
        val_results = m.val(
            data=str(root),
            split="val",
            imgsz=imgsz,
            batch=batch,
            device=device,
            amp=_use_amp(device),
        )
        val_metrics = val_results.results_dict

    return {
        "save_dir": save_dir,
        "best_weights": best_weights,
        "train_results": train_results,
        "val_metrics": val_metrics,
    }


def _expand_xyxy(
    x1: float,
    y1: float,
    x2: float,
    y2: float,
    w: int,
    h: int,
    margin: float = 0.05,
) -> tuple[int, int, int, int]:
    bw = x2 - x1
    bh = y2 - y1
    mx = bw * margin
    my = bh * margin
    nx1 = int(max(0, np.floor(x1 - mx)))
    ny1 = int(max(0, np.floor(y1 - my)))
    nx2 = int(min(w - 1, np.ceil(x2 + mx)))
    ny2 = int(min(h - 1, np.ceil(y2 + my)))
    if nx2 <= nx1:
        nx2 = min(w - 1, nx1 + 1)
    if ny2 <= ny1:
        ny2 = min(h - 1, ny1 + 1)
    return nx1, ny1, nx2, ny2


def run_three_stage_defect_pipeline(
    image: str | Path | np.ndarray,
    object_detector_weights: str | Path,
    defect_detector_weights: str | Path,
    defect_classifier_weights: str | Path,
    object_class_ids: tuple[int, ...] | None = (0,),
    conf_obj: float = 0.25,
    conf_def: float = 0.25,
    conf_cls: float = 0.25,
    crop_margin: float = 0.05,
    device: str | None = None,
) -> dict[str, Any]:
    """
    Основная архитектура:
    1) Детекция напечатанного объекта (YOLOv9).
    2) Детекция дефектов на вырезке объекта (YOLOv9).
    3) Классификация типа каждого дефекта (YOLO11-cls).

    object_class_ids — id классов bbox, которые считаются «объектом печати»
    (по умолчанию 0; при разметке model_presence обычно 0 = 3D_model).

    Возвращает словарь с подсчётом типов дефектов и деталями по каждому экземпляру.
    """
    if isinstance(image, (str, Path)):
        bgr = cv2.imread(str(image))
        if bgr is None:
            raise FileNotFoundError(f"Не удалось прочитать изображение: {image}")
    else:
        bgr = image

    h, w = bgr.shape[:2]
    predict_kw: dict[str, Any] = {"conf": conf_obj, "verbose": False}
    if device is not None:
        predict_kw["device"] = device

    obj_model = YOLO(str(object_detector_weights))
    def_model = YOLO(str(defect_detector_weights))
    cls_model = YOLO(str(defect_classifier_weights))

    obj_res = obj_model.predict(bgr, **predict_kw)[0]
    if obj_res.boxes is None or len(obj_res.boxes) == 0:
        return {
            "object_found": False,
            "defect_counts": {},
            "total_defects": 0,
            "details": [],
        }

    allowed = set(object_class_ids) if object_class_ids is not None else None
    best_idx = -1
    best_area = -1.0
    xyxy_all = obj_res.boxes.xyxy.cpu().numpy()
    cls_all = obj_res.boxes.cls.cpu().numpy().astype(int)

    for i, c in enumerate(cls_all):
        if allowed is not None and c not in allowed:
            continue
        x1, y1, x2, y2 = xyxy_all[i]
        area = float((x2 - x1) * (y2 - y1))
        if area > best_area:
            best_area = area
            best_idx = i

    if best_idx < 0:
        return {
            "object_found": False,
            "defect_counts": {},
            "total_defects": 0,
            "details": [],
        }

    ox1, oy1, ox2, oy2 = xyxy_all[best_idx]
    cx1, cy1, cx2, cy2 = _expand_xyxy(ox1, oy1, ox2, oy2, w, h, crop_margin)
    crop = bgr[cy1:cy2, cx1:cx2]
    if crop.size == 0:
        return {
            "object_found": True,
            "defect_counts": {},
            "total_defects": 0,
            "details": [],
            "object_bbox_xyxy": [float(ox1), float(oy1), float(ox2), float(oy2)],
        }

    def_kw: dict[str, Any] = {"conf": conf_def, "verbose": False}
    if device is not None:
        def_kw["device"] = device
    def_res = def_model.predict(crop, **def_kw)[0]

    details: list[dict[str, Any]] = []
    if def_res.boxes is None or len(def_res.boxes) == 0:
        return {
            "object_found": True,
            "defect_counts": {},
            "total_defects": 0,
            "details": [],
            "object_bbox_xyxy": [float(ox1), float(oy1), float(ox2), float(oy2)],
            "crop_bbox_xyxy": [cx1, cy1, cx2, cy2],
        }

    d_xyxy = def_res.boxes.xyxy.cpu().numpy()
    d_cls = def_res.boxes.cls.cpu().numpy().astype(int)
    d_conf = def_res.boxes.conf.cpu().numpy()
    det_names = def_res.names

    cls_kw: dict[str, Any] = {"conf": conf_cls, "verbose": False}
    if device is not None:
        cls_kw["device"] = device

    labels_for_counter: list[str] = []

    for i in range(len(d_xyxy)):
        dx1, dy1, dx2, dy2 = d_xyxy[i]
        di1 = int(max(0, np.floor(dx1)))
        dj1 = int(max(0, np.floor(dy1)))
        di2 = int(min(crop.shape[1] - 1, np.ceil(dx2)))
        dj2 = int(min(crop.shape[0] - 1, np.ceil(dy2)))
        if di2 <= di1 or dj2 <= dj1:
            continue
        roi = crop[dj1:dj2, di1:di2]
        if roi.size == 0:
            continue

        cls_out = cls_model.predict(roi, **cls_kw)[0]
        if cls_out.probs is None:
            det_label = det_names.get(int(d_cls[i]), str(int(d_cls[i])))
            labels_for_counter.append(det_label)
            gx1 = cx1 + di1
            gy1 = cy1 + dj1
            gx2 = cx1 + di2
            gy2 = cy1 + dj2
            details.append(
                {
                    "defect_bbox_xyxy_global": [gx1, gy1, gx2, gy2],
                    "detection_class_id": int(d_cls[i]),
                    "detection_label": det_label,
                    "detection_conf": float(d_conf[i]),
                    "classified_label": None,
                    "classification_conf": None,
                }
            )
            continue

        top1 = int(cls_out.probs.top1)
        top1_conf = float(cls_out.probs.top1conf)
        cname = cls_out.names[top1]
        labels_for_counter.append(cname)

        gx1 = cx1 + di1
        gy1 = cy1 + dj1
        gx2 = cx1 + di2
        gy2 = cy1 + dj2
        details.append(
            {
                "defect_bbox_xyxy_global": [gx1, gy1, gx2, gy2],
                "detection_class_id": int(d_cls[i]),
                "detection_label": det_names.get(int(d_cls[i]), str(int(d_cls[i]))),
                "detection_conf": float(d_conf[i]),
                "classified_label": cname,
                "classification_conf": top1_conf,
            }
        )

    counts = dict(Counter(labels_for_counter))
    return {
        "object_found": True,
        "defect_counts": counts,
        "total_defects": len(labels_for_counter),
        "details": details,
        "object_bbox_xyxy": [float(ox1), float(oy1), float(ox2), float(oy2)],
        "crop_bbox_xyxy": [cx1, cy1, cx2, cy2],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="YOLOv9 detection, YOLO11 classification, three-stage pipeline."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_obj = sub.add_parser("train-object", help="Train YOLOv9 object presence detector.")
    p_obj.add_argument(
        "--data",
        type=str,
        default="datasets/FDM-3D-Printing-Defect-Dataset/model_presence/data.yaml",
    )
    p_obj.add_argument("--model", type=str, default="yolov9c.pt")
    _add_train_args(p_obj)

    p_def = sub.add_parser("train-defect", help="Train YOLOv9 defect detector.")
    p_def.add_argument(
        "--data",
        type=str,
        default="datasets/FDM-3D-Printing-Defect-Dataset/defect_type/data.yaml",
    )
    p_def.add_argument("--model", type=str, default="yolov9c.pt")
    _add_train_args(p_def)

    p_cls = sub.add_parser("train-cls", help="Train YOLO11 defect classifier.")
    p_cls.add_argument(
        "--data",
        type=str,
        default="datasets/FDM-3D-Printing-Defect-Dataset/defect_classification",
    )
    p_cls.add_argument("--model", type=str, default="yolo11n-cls.pt")
    p_cls.add_argument("--epochs", type=int, default=20)
    p_cls.add_argument("--imgsz", type=int, default=224)
    p_cls.add_argument("--batch", type=int, default=32)
    p_cls.add_argument("--workers", type=int, default=8)
    p_cls.add_argument("--project", type=str, default="runs/yolo11_cls")
    p_cls.add_argument("--name", type=str, default="defect_classification")
    p_cls.add_argument("--device", type=str, default="0")
    p_cls.add_argument("--patience", type=int, default=30)

    p_pipe = sub.add_parser("pipeline", help="Run 3-stage inference on one image.")
    p_pipe.add_argument("--image", type=str, required=True)
    p_pipe.add_argument(
        "--weights-obj",
        type=str,
        required=True,
        help="Path to object detector best.pt",
    )
    p_pipe.add_argument(
        "--weights-def",
        type=str,
        required=True,
        help="Path to defect detector best.pt",
    )
    p_pipe.add_argument(
        "--weights-cls",
        type=str,
        required=True,
        help="Path to YOLO11 classifier best.pt",
    )
    p_pipe.add_argument(
        "--object-class-ids",
        type=str,
        default="0",
        help="Comma-separated class ids treated as printed object (e.g. 0 for 3D_model)",
    )
    p_pipe.add_argument("--conf-obj", type=float, default=0.25)
    p_pipe.add_argument("--conf-def", type=float, default=0.25)
    p_pipe.add_argument("--conf-cls", type=float, default=0.25)
    p_pipe.add_argument("--device", type=str, default=None)

    return parser.parse_args()


def _add_train_args(p: argparse.ArgumentParser) -> None:
    p.add_argument("--epochs", type=int, default=20)
    p.add_argument("--imgsz", type=int, default=640)
    p.add_argument("--batch", type=int, default=16)
    p.add_argument("--workers", type=int, default=8)
    p.add_argument("--project", type=str, default="runs/yolov9")
    p.add_argument("--name", type=str, default="train")
    p.add_argument("--device", type=str, default="0")
    p.add_argument("--patience", type=int, default=30)
    p.add_argument("--freeze", type=int, default=0)


def main() -> None:
    args = parse_args()

    if args.command == "train-object":
        out = train_yolov9_detection(
            data_yaml=args.data,
            weights=args.model,
            epochs=args.epochs,
            imgsz=args.imgsz,
            batch=args.batch,
            workers=args.workers,
            project=args.project,
            name=args.name,
            device=args.device,
            patience=args.patience,
            freeze=args.freeze,
        )
    elif args.command == "train-defect":
        out = train_yolov9_defect_detection(
            data_yaml=args.data,
            weights=args.model,
            epochs=args.epochs,
            imgsz=args.imgsz,
            batch=args.batch,
            workers=args.workers,
            project=args.project,
            name=args.name,
            device=args.device,
            patience=args.patience,
            freeze=args.freeze,
        )
    elif args.command == "train-cls":
        out = train_yolo11_defect_classification(
            data_dir=args.data,
            model=args.model,
            epochs=args.epochs,
            imgsz=args.imgsz,
            batch=args.batch,
            workers=args.workers,
            project=args.project,
            name=args.name,
            device=args.device,
            patience=args.patience,
        )
    elif args.command == "pipeline":
        ids = tuple(
            int(x.strip()) for x in args.object_class_ids.split(",") if x.strip()
        )
        result = run_three_stage_defect_pipeline(
            image=args.image,
            object_detector_weights=args.weights_obj,
            defect_detector_weights=args.weights_def,
            defect_classifier_weights=args.weights_cls,
            object_class_ids=ids if ids else (0,),
            conf_obj=args.conf_obj,
            conf_def=args.conf_def,
            conf_cls=args.conf_cls,
            device=args.device,
        )
        print(result)
        return
    else:
        raise SystemExit(f"Unknown command: {args.command}")

    print(f"Training run saved to: {out['save_dir']}")
    print(f"Best weights: {out['best_weights']}")
    if out.get("val_metrics") is not None:
        print(f"Validation metrics: {out['val_metrics']}")


if __name__ == "__main__":
    main()
