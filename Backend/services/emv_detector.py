"""Ambulance detection backed by a model trained for ambulance labels.

COCO YOLO has no ambulance class: class 5 is a bus, so it must never be used
to trigger an emergency traffic signal.
"""

import os
from pathlib import Path

from ultralytics import YOLO

DEFAULT_LABELS = {"ambulance", "emergency vehicle", "emergency_vehicle"}


class EmergencyDetector:
    def __init__(self, model_path=None, confidence=None):
        default_path = Path(__file__).resolve().parents[1] / "models" / "ambulance.pt"
        self.model_path = Path(model_path or os.getenv("EMERGENCY_MODEL_PATH", default_path))
        # Demo-camera video is compressed and distant; 0.45 retains the
        # ambulance detections validated against the bundled lane footage.
        self.confidence = confidence or float(os.getenv("EMERGENCY_CONFIDENCE", "0.45"))
        self.model, self.class_ids, self.error = None, set(), None
        if not self.model_path.is_file():
            self.error = f"Ambulance model not found: {self.model_path}"
            return
        try:
            self.model = YOLO(str(self.model_path))
            allowed = {x.strip().lower() for x in os.getenv("EMERGENCY_CLASS_NAMES", "").split(",") if x.strip()} or DEFAULT_LABELS
            self.class_ids = {int(i) for i, name in self.model.names.items() if str(name).strip().lower() in allowed}
            if not self.class_ids:
                self.error = "Ambulance label missing; set EMERGENCY_CLASS_NAMES to the model label."
                self.model = None
        except Exception as exc:
            self.error = f"Unable to load ambulance model: {exc}"

    @property
    def available(self):
        return self.model is not None and bool(self.class_ids)

    def detect(self, frame):
        if not self.available:
            return []
        result = self.model(frame, conf=self.confidence, verbose=False)[0]
        return [
            (box.xyxy[0].tolist(), float(box.conf[0]), "ambulance")
            for box in result.boxes
            if int(box.cls[0]) in self.class_ids
        ]
