from __future__ import annotations

import threading
import time
from pathlib import Path

import cv2
from ultralytics import YOLO

from services.emv_detector import EmergencyDetector

MODEL_PATH = Path(__file__).resolve().parents[1] / "yolov8n.pt"
VEHICLE_CLASS_IDS = {2, 3, 5, 7}  # COCO: car, motorcycle, bus, truck
EMERGENCY_HOLD_SECONDS = 30.0
# Every dashboard stream uses the same pixel dimensions. Source camera files
# have different resolutions, so rendering at a fixed size keeps labels and
# boxes visually consistent across all lanes.
DISPLAY_FRAME_WIDTH = 960
DISPLAY_FRAME_HEIGHT = 540


class TrafficAnalyzer:
    """The backend is the sole authority for detection and traffic lights."""

    def __init__(self, lane_videos, vehicle_model=None, emergency_detector=None, start_workers=True):
        self.lock = threading.RLock()
        self.vehicle_model = vehicle_model or YOLO(str(MODEL_PATH))
        self.emergency_detector = emergency_detector or EmergencyDetector()
        self.lanes = {
            lane: {
                "video": cv2.VideoCapture(str(path)) if Path(path).exists() else None,
                "light": "red", "timer": 10, "vehicles": 0,
                "emv_detected": False, "emergency_confidence": 0.0,
                "emergency_hits": 0, "emergency_until": 0.0,
                "violators": [], "frame": None,
            }
            for lane, path in lane_videos.items()
        }
        self.stc_enabled, self.active_lane = True, None
        self.emergency_lane = None
        if start_workers:
            # One round-robin worker prevents one short video or a slow model
            # call from starving the other lane streams.
            threading.Thread(target=self._process_all_lanes, daemon=True).start()

    def _process_all_lanes(self):
        while True:
            processed_frame = False
            for lane, data in self.lanes.items():
                cap = data["video"]
                if cap is None or not cap.isOpened():
                    continue
                ok, frame = cap.read()
                if not ok:
                    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    ok, frame = cap.read()
                if ok:
                    self.process_frame(lane, frame)
                    processed_frame = True
            # Camera files should never consume an entire CPU core, while live
            # cameras still get a chance to be processed every round.
            time.sleep(0.03 if processed_frame else 0.25)

    def _process_lane(self, lane):
        """Legacy single-lane worker retained for direct integrations."""
        cap = self.lanes[lane]["video"]
        if cap is None or not cap.isOpened():
            return
        while True:
            ok, frame = cap.read()
            if not ok:
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue
            self.process_frame(lane, frame)
            time.sleep(0.10)  # local videos must not loop at CPU speed

    def process_frame(self, lane, frame):
        """Process one frame; public to make the priority policy testable."""
        with self.lock:
            vehicle_result = self.vehicle_model(frame, verbose=False)[0]
            vehicles = sum(int(box.cls[0]) in VEHICLE_CLASS_IDS for box in vehicle_result.boxes)
            emergency_boxes = self.emergency_detector.detect(frame)
            now, data = time.monotonic(), self.lanes[lane]
            if emergency_boxes:
                data["emergency_hits"] += 1
                data["emergency_confidence"] = max(item[1] for item in emergency_boxes)
                # The emergency model has an explicit Ambulance class. Open
                # the detected lane immediately, then retain that priority
                # through brief missed frames in compressed camera footage.
                data["emergency_until"] = now + EMERGENCY_HOLD_SECONDS
                # Do not let the next camera frame overwrite an active
                # emergency route when multiple lanes contain ambulances.
                if self.emergency_lane is None or not self.lanes[self.emergency_lane]["emv_detected"]:
                    self.emergency_lane = lane
            else:
                data["emergency_hits"] = 0
                if now >= data["emergency_until"]:
                    data["emergency_confidence"] = 0.0
            data.update({
                "vehicles": vehicles,
                "frame": self._annotate_frame(frame, vehicle_result, emergency_boxes),
                "timer": min(60, 10 + vehicles * 2),
                "emv_detected": now < data["emergency_until"],
            })
            self._apply_signal_policy()

    @staticmethod
    def _overlaps_emergency(vehicle_xyxy, emergency_xyxy):
        """Match a COCO vehicle box to an ambulance box without class guessing."""
        vx1, vy1, vx2, vy2 = vehicle_xyxy
        ex1, ey1, ex2, ey2 = emergency_xyxy
        ix1, iy1 = max(vx1, ex1), max(vy1, ey1)
        ix2, iy2 = min(vx2, ex2), min(vy2, ey2)
        intersection = max(0, ix2 - ix1) * max(0, iy2 - iy1)
        vehicle_area = max(1, (vx2 - vx1) * (vy2 - vy1))
        emergency_area = max(1, (ex2 - ex1) * (ey2 - ey1))
        vehicle_center = ((vx1 + vx2) / 2, (vy1 + vy2) / 2)
        emergency_center = ((ex1 + ex2) / 2, (ey1 + ey2) / 2)
        center_contained = (
            ex1 <= vehicle_center[0] <= ex2 and ey1 <= vehicle_center[1] <= ey2
        ) or (
            vx1 <= emergency_center[0] <= vx2 and vy1 <= emergency_center[1] <= vy2
        )
        return center_contained or intersection / min(vehicle_area, emergency_area) >= 0.25

    def _annotate_frame(self, frame, vehicle_result, emergency_boxes):
        """Render ambulance boxes last and suppress their COCO truck/car label."""
        annotated = frame.copy()
        emergency_coordinates = [box[0] for box in emergency_boxes]
        for box in vehicle_result.boxes:
            cls = int(box.cls[0])
            xyxy = [int(value) for value in box.xyxy[0].tolist()]
            if any(self._overlaps_emergency(xyxy, emergency) for emergency in emergency_coordinates):
                continue
            x1, y1, x2, y2 = xyxy
            label = self.vehicle_model.names[cls]
            confidence = float(box.conf[0])
            cv2.rectangle(annotated, (x1, y1), (x2, y2), (255, 255, 255), 2)
            self._draw_label(
                annotated,
                f"{label.upper()} {confidence:.0%}",
                x1,
                y1,
                background=(45, 45, 45),
                font_scale=0.72,
            )
        for xyxy, confidence, _ in emergency_boxes:
            x1, y1, x2, y2 = map(int, xyxy)
            cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 0, 255), 4)
            self._draw_label(
                annotated,
                f"AMBULANCE {confidence:.0%}",
                x1,
                y1,
                background=(0, 0, 255),
                font_scale=0.95,
            )
        return cv2.resize(
            annotated,
            (DISPLAY_FRAME_WIDTH, DISPLAY_FRAME_HEIGHT),
            interpolation=cv2.INTER_LINEAR,
        )

    @staticmethod
    def _draw_label(image, text, x, y, background, font_scale):
        """Draw a high-contrast label that stays readable in the dashboard feed."""
        font, thickness, padding = cv2.FONT_HERSHEY_SIMPLEX, 2, 6
        (width, height), baseline = cv2.getTextSize(text, font, font_scale, thickness)
        top = max(0, y - height - baseline - padding * 2)
        right = min(image.shape[1], x + width + padding * 2)
        cv2.rectangle(image, (x, top), (right, y), background, -1)
        cv2.putText(image, text, (x + padding, y - baseline - padding), font, font_scale, (255, 255, 255), thickness, cv2.LINE_AA)

    def _apply_signal_policy(self):
        if not self.stc_enabled or not self.lanes:
            return
        emergency_lanes = [lane for lane, data in self.lanes.items() if data["emv_detected"]]
        if self.emergency_lane in emergency_lanes:
            selected = self.emergency_lane
        elif emergency_lanes:
            selected = max(emergency_lanes, key=lambda lane: self.lanes[lane]["emergency_confidence"])
            self.emergency_lane = selected
        else:
            self.emergency_lane = None
            selected = max(self.lanes, key=lambda lane: self.lanes[lane]["vehicles"])
        self.active_lane = selected
        for lane, data in self.lanes.items():
            data["light"] = "green" if lane == selected else "red"

    def get_status(self):
        with self.lock:
            return {lane: {"light": data["light"], "timer": data["timer"], "vehicles": data["vehicles"], "emv_detected": data["emv_detected"], "emergency_confidence": round(data["emergency_confidence"], 3), "violators": data["violators"]} for lane, data in self.lanes.items()}

    def get_frame(self, lane):
        with self.lock:
            return self.lanes.get(lane, {}).get("frame")

    def update_light(self, lane, state):
        if lane not in self.lanes or state not in {"red", "yellow", "green"}:
            return "Invalid lane or light state"
        with self.lock:
            self.stc_enabled = False
            if state == "green":
                self.active_lane = lane
                for name, data in self.lanes.items():
                    data["light"] = "green" if name == lane else "red"
            else:
                self.lanes[lane]["light"] = state
        return f"{lane} changed to {state}"

    def toggle_stc(self, enable):
        with self.lock:
            self.stc_enabled = bool(enable)
            if self.stc_enabled:
                self._apply_signal_policy()
            return self.stc_enabled

    def check_emv(self):
        with self.lock:
            return [lane for lane, data in self.lanes.items() if data["emv_detected"]]

    def clear_for_emv(self):
        with self.lock:
            self._apply_signal_policy()
            return self.active_lane


lane_videos = {f"lane{i}": Path(__file__).resolve().parents[1] / "videos" / f"lane{i}.mp4" for i in range(1, 5)}
traffic_service = TrafficAnalyzer(lane_videos)
