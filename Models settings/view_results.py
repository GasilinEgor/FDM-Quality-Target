import os
import cv2
import glob
from pathlib import Path

def get_images_path(folder_path):
    image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.JPG', '*.PNG']
    image_paths = []
    for ext in image_extensions:
        image_paths.extend(glob.glob(os.path.join(folder_path, ext)))

    if not image_paths:
        print("В папке нет изображений!")
        return []
    else:
        return image_paths

def get_boxes_path(folder_path):
    box_paths = []
    for file in ['*.txt']:
        box_paths.extend(glob.glob(os.path.join(folder_path, file)))
    if not box_paths:
        print("В папке нет ффайлов пометок!")
        return 
    else:
        return box_paths


def show_images_sequentially(img_path, box_path): 
    current_index = 0
    
    while True:
        img = cv2.imread(img_path[current_index])
        
        if img is None:
            print(f"Не удалось загрузить {img_path[current_index]}")
            current_index = (current_index + 1) % len(img_path)
            continue

        img_h, img_w = img.shape[:2]

        with open(box_path[current_index], 'r', encoding='utf-8') as box_file:
            boxes = box_file.readlines()
        window_name = f"Изображение {current_index + 1}/{len(img_path)}: {img_path[current_index]}"
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(window_name, 800, 800)
        for box in boxes:
            line = box.strip()
            if not line or line.startswith('#'):
                continue
            data = line.split()
            if len(data) < 5:
                continue
            defect_num = int(float(data[0]))
            x_center, y_center, width, height = map(float, data[1:5])
            x1 = (x_center - width / 2) * img_w
            y1 = (y_center - height / 2) * img_h
            x2 = (x_center + width / 2) * img_w
            y2 = (y_center + height / 2) * img_h
            x1i = int(round(max(0, min(x1, img_w - 1))))
            y1i = int(round(max(0, min(y1, img_h - 1))))
            x2i = int(round(max(0, min(x2, img_w - 1))))
            y2i = int(round(max(0, min(y2, img_h - 1))))
            cv2.rectangle(img, pt1=(x1i, y1i), pt2=(x2i, y2i), color=(255, 0, 0), thickness=2)
        cv2.imshow(window_name, img)
        
        print(f"\nТекущее: {img_path[current_index]} ({current_index + 1}/{len(img_path)})")
        print("Нажмите:")
        print("  ПРОБЕЛ или ПРАВАЯ СТРЕЛКА - следующее изображение")
        print("  ЛЕВАЯ СТРЕЛКА - предыдущее изображение") 
        print("  ESC или q - выход")
        
        key = cv2.waitKey(0) & 0xFF
        
        cv2.destroyAllWindows()
        
        if key == 27 or key == ord('q'): 
            print("Просмотр завершен!")
            break
        elif key == ord(' ') or key == 81 or key == 83:
            current_index = (current_index + 1) % len(img_path)
        elif key == 81:
            current_index = (current_index - 1) % len(img_path)
    
    cv2.destroyAllWindows()


def _image_to_fit_max_side(img, max_w, max_h):
    if img is None:
        return None
    h, w = img.shape[:2]
    if w <= 0 or h <= 0:
        return None
    scale = min(max_w / w, max_h / h)
    nw = max(1, int(round(w * scale)))
    nh = max(1, int(round(h * scale)))
    interp = cv2.INTER_AREA if scale < 1.0 else cv2.INTER_LINEAR
    return cv2.resize(img, (nw, nh), interpolation=interp)


def _save_yolo_labels(label_path, boxes, img_w, img_h):
    lines = []
    for class_id, x1, y1, x2, y2 in boxes:
        x1 = max(0, min(x1, img_w - 1))
        y1 = max(0, min(y1, img_h - 1))
        x2 = max(0, min(x2, img_w - 1))
        y2 = max(0, min(y2, img_h - 1))
        if x2 <= x1 or y2 <= y1:
            continue
        xc = ((x1 + x2) / 2.0) / img_w
        yc = ((y1 + y2) / 2.0) / img_h
        bw = (x2 - x1) / img_w
        bh = (y2 - y1) / img_h
        lines.append(f"{class_id} {xc:.6f} {yc:.6f} {bw:.6f} {bh:.6f}")
    with open(label_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def _load_yolo_labels(label_path, img_w, img_h):
    boxes = []
    if not os.path.exists(label_path):
        return boxes
    with open(label_path, "r", encoding="utf-8") as f:
        for raw_line in f:
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split()
            if len(parts) < 5:
                continue
            class_id = int(float(parts[0]))
            xc, yc, bw, bh = map(float, parts[1:5])
            x1 = int(round((xc - bw / 2.0) * img_w))
            y1 = int(round((yc - bh / 2.0) * img_h))
            x2 = int(round((xc + bw / 2.0) * img_w))
            y2 = int(round((yc + bh / 2.0) * img_h))
            boxes.append((class_id, x1, y1, x2, y2))
    return boxes


def _write_dataset_yaml(dataset_root, class_names):
    yaml_path = os.path.join(dataset_root, "data.yaml")
    content = [
        f"path: {dataset_root.replace(os.sep, '/')}",
        "train: images",
        "val: images",
        "test: images",
        "",
        f"nc: {len(class_names)}",
        "names:",
    ]
    for idx, name in enumerate(class_names):
        content.append(f"  {idx}: {name}")
    with open(yaml_path, "w", encoding="utf-8") as f:
        f.write("\n".join(content) + "\n")


def view_defects_img():
    MAX_W, MAX_H = 800, 800
    DEFECTS_TYPES = ['Cracking', 'Layer_shifting', 'Off_platform', 'Stringing', 'Warping']
    dataset_root = os.path.join("datasets", "FDM-3D-Printing-Defect-Dataset")
    labels_root = os.path.join(dataset_root, "labels")
    os.makedirs(labels_root, exist_ok=True)
    _write_dataset_yaml(dataset_root, DEFECTS_TYPES)

    class_colors = [
        (0, 255, 255),
        (0, 255, 0),
        (255, 255, 0),
        (255, 0, 255),
        (0, 128, 255),
    ]
    image_entries = []
    for defect_type in DEFECTS_TYPES:
        img_folder_path = os.path.join(dataset_root, "data", defect_type)
        for img_path in get_images_path(img_folder_path):
            image_entries.append((img_path, defect_type))

    if not image_entries:
        print("Изображения для разметки не найдены.")
        return

    win = "Разметка дефектов"
    cv2.namedWindow(win, cv2.WINDOW_NORMAL)
    current_index = 0

    while True:
        img_path, defect_type = image_entries[current_index]
        print(f"[{current_index + 1}/{len(image_entries)}] {img_path}")
        img = cv2.imread(img_path)
        if img is None:
            print(f"Не удалось загрузить {img_path}")
            current_index = (current_index + 1) % len(image_entries)
            continue

        img_h, img_w = img.shape[:2]
        scale = min(MAX_W / img_w, MAX_H / img_h)
        disp_w = max(1, int(round(img_w * scale)))
        disp_h = max(1, int(round(img_h * scale)))
        interp = cv2.INTER_AREA if scale < 1.0 else cv2.INTER_LINEAR

        label_dir = os.path.join(labels_root, defect_type)
        os.makedirs(label_dir, exist_ok=True)
        label_path = os.path.join(label_dir, f"{Path(img_path).stem}.txt")
        boxes = _load_yolo_labels(label_path, img_w, img_h)
        active_class = DEFECTS_TYPES.index(defect_type)

        state = {"drawing": False, "start": (0, 0), "current": (0, 0)}

        def draw_frame():
            disp = cv2.resize(img, (disp_w, disp_h), interpolation=interp)
            for class_id, x1, y1, x2, y2 in boxes:
                color = class_colors[class_id % len(class_colors)]
                dx1 = int(round(x1 * scale))
                dy1 = int(round(y1 * scale))
                dx2 = int(round(x2 * scale))
                dy2 = int(round(y2 * scale))
                cv2.rectangle(disp, (dx1, dy1), (dx2, dy2), color, 2)
                label = DEFECTS_TYPES[class_id]
                cv2.putText(
                    disp,
                    label,
                    (dx1, max(20, dy1 - 8)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    color,
                    1,
                    cv2.LINE_AA,
                )

            if state["drawing"]:
                sx, sy = state["start"]
                cx, cy = state["current"]
                cv2.rectangle(disp, (sx, sy), (cx, cy), class_colors[active_class], 1)

            help_line = (
                f"[{current_index + 1}/{len(image_entries)}] "
                f"Class {active_class}:{DEFECTS_TYPES[active_class]} | "
                "1..5 class, drag box, s save, u undo, space/-> next, <- prev, q/esc exit"
            )
            cv2.putText(
                disp,
                help_line,
                (10, max(20, disp_h - 10)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.45,
                (255, 255, 255),
                1,
                cv2.LINE_AA,
            )
            cv2.imshow(win, disp)

        def mouse_callback(event, x, y, flags, param):
            if event == cv2.EVENT_LBUTTONDOWN:
                state["drawing"] = True
                state["start"] = (x, y)
                state["current"] = (x, y)
            elif event == cv2.EVENT_MOUSEMOVE and state["drawing"]:
                state["current"] = (x, y)
                draw_frame()
            elif event == cv2.EVENT_LBUTTONUP and state["drawing"]:
                state["drawing"] = False
                x0, y0 = state["start"]
                x1d, y1d = x, y
                left, right = sorted((x0, x1d))
                top, bottom = sorted((y0, y1d))
                if (right - left) >= 4 and (bottom - top) >= 4:
                    ox1 = int(round(left / scale))
                    oy1 = int(round(top / scale))
                    ox2 = int(round(right / scale))
                    oy2 = int(round(bottom / scale))
                    boxes.append((active_class, ox1, oy1, ox2, oy2))
                draw_frame()

        cv2.setMouseCallback(win, mouse_callback)
        draw_frame()
        cv2.resizeWindow(win, disp_w, disp_h)

        nav = "stay"
        while True:
            key = cv2.waitKey(20) & 0xFF
            if key == 255:
                continue
            if key in (27, ord('q')):
                _save_yolo_labels(label_path, boxes, img_w, img_h)
                nav = "exit"
                break
            if ord('1') <= key <= ord(str(len(DEFECTS_TYPES))):
                active_class = key - ord('1')
                draw_frame()
                continue
            if key == ord('u'):
                if boxes:
                    boxes.pop()
                    draw_frame()
                continue
            if key == ord('s'):
                _save_yolo_labels(label_path, boxes, img_w, img_h)
                print(f"Сохранено: {label_path}")
                draw_frame()
                continue
            if key in (ord(' '), 83):
                _save_yolo_labels(label_path, boxes, img_w, img_h)
                nav = "next"
                break
            if key == 81:
                _save_yolo_labels(label_path, boxes, img_w, img_h)
                nav = "prev"
                break

        if nav == "exit":
            break
        if nav == "next":
            current_index = (current_index + 1) % len(image_entries)
        elif nav == "prev":
            current_index = (current_index - 1) % len(image_entries)

    cv2.destroyWindow(win)
    cv2.destroyAllWindows()


def view_roboflow_dataset():
    img_folder_path = "datasets/roboflow/test/images"
    box_folder_path = "datasets/roboflow/test/labels"
    img_path = get_images_path(img_folder_path)
    box_path = get_boxes_path(box_folder_path)
    show_images_sequentially(img_path, box_path)


def main():
    view_defects_img()
    

if __name__ == "__main__":
    main()
