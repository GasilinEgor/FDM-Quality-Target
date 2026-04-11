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


def main():
    img_folder_path = "datasets/roboflow/test/images"
    box_folder_path = "datasets/roboflow/test/labels"
    img_path = get_images_path(img_folder_path)
    box_path = get_boxes_path(box_folder_path)
    show_images_sequentially(img_path, box_path)
    

if __name__ == "__main__":
    main()
