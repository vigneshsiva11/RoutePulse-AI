from ultralytics import YOLO
import cv2

model = YOLO("yolov8n.pt")  # base model (fine-tune later)


def detect_emv(video_path):
    cap = cv2.VideoCapture(video_path)
    results_data = {"vehicles": 0, "emergency_detected": False, "violators": []}

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        results = model(frame, verbose=False)
        for r in results:
            for cls in r.boxes.cls:
                if int(cls) in [2, 3, 5, 7]:  # car, bus, truck, etc.
                    results_data["vehicles"] += 1
                if (
                    int(cls) == 5
                ):  # say class 5 = ambulance (need custom dataset ideally)
                    results_data["emergency_detected"] = True

    cap.release()
    return results_data
