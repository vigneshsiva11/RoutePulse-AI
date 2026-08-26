import cv2
import easyocr

reader = easyocr.Reader(["en"])


def detect_number_plate(image_path):
    img = cv2.imread(image_path)
    results = reader.readtext(img)

    detected_plates = []
    for bbox, text, prob in results:
        if prob > 0.5:  # confidence threshold
            detected_plates.append(text)

    return detected_plates
