from ultralytics import YOLO
from patched_yolo_infer import visualize_results_usual_yolo_inference
import cv2
from PIL import Image
from math import sqrt


model = YOLO("best.pt")


def calculate_center(xyxy):
    x_center = (xyxy[0] + xyxy[2]) / 2
    y_center = (xyxy[1] + xyxy[3]) / 2
    return x_center, y_center

def check_spaces(img_path) -> str:
    """Проверяем наличие свободных мест по расстоянию между центрами прямоугольников."""
    results = model(img_path)
    occupied_centers = []
    for result in results:
        for box in result.boxes:
            conf = box.conf.item()
            cls_name = model.names[box.cls[0].item()]
            if conf >= 0.25 and cls_name == "Occupied":
                center = calculate_center(box.xyxy[0].tolist())
                occupied_centers.append(center)

    occupied_centers.sort(key=lambda c: (c[1], c[0]))  # Сортировка по y, затем x для устойчивой проверки

    # Проверка на наличие больших промежутков между машинами
    for i in range(len(occupied_centers) - 1):
        x1, y1 = occupied_centers[i]
        x2, y2 = occupied_centers[i + 1]
        dist = sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

        if dist > 250:  # Настраиваемый параметр для "свободного места"
            return True

    # Дополнительная проверка: большое расстояние от машины до края изображения
    if occupied_centers:
        first_y = occupied_centers[0][1]
        last_y = occupied_centers[-1][1]
        image = Image.open(img_path)
        width, height = image.size

        if first_y > 250 or height - last_y > 250:
            return True

    return False


def make_photo(image_path,url):
    """Сделать фото с камеры и обрезать его."""
    # RTSP-URL камеры
    rtsp_url = url

    # Подключение к камере
    cap = cv2.VideoCapture(rtsp_url)

    if not cap.isOpened():
        print("Не удалось подключиться к камере.")
    else:
        # Чтение первого кадра
        ret, frame = cap.read()
        if ret:
            # Сохранение изображения
            cv2.imwrite(image_path, frame)
            print("Изображение сохранено как camera_snapshot.jpg")
        else:
            print("Не удалось получить кадр.")

    # Освобождение ресурсов
    cap.release()

    # Загрузка изображения
    image = Image.open(image_path)

    # Получите размеры изображения
    width, height = image.size

    mid_point = height // 2

    # Сохраните обрезанное изображение
    image = image.crop((794,0,1062,850))
    width, height = image.size
    image.save(image_path)

    print(f"Изображение обрезано и сохранено как {image_path}")


def detect_cars(img_path, url) -> bool:
    make_photo(img_path, url)
    img = cv2.imread(img_path)
    if img is None:
        print("Не удалось загрузить изображение.")
        return False

    result_text = check_spaces(img_path)
    print("Результат анализа:", result_text)
    if result_text:
        return True
    return False