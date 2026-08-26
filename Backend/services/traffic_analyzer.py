from ultralytics import YOLO
import cv2, time
import threading


model = YOLO("yolov8n.pt")  # lightweight model


class TrafficAnalyzer:
    def __init__(self, lane_videos):
        self.lanes = {
            lane: {
                "video": cv2.VideoCapture(path),
                "light": "red",
                "timer": 0,  # start as 0, will be updated dynamically
                "vehicles": 0,
                "emv_detected": False,
                "violators": [],
                "frame": None,
            }
            for lane, path in lane_videos.items()
        }
        self.stc_enabled = True

        # start background threads
        for lane in self.lanes:
            t = threading.Thread(target=self._process_lane, args=(lane,), daemon=True)
            t.start()

    def _process_lane(self, lane):
        cap = self.lanes[lane]["video"]
        while True:
            ret, frame = cap.read()
            if not ret:
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue

            results = model(frame, verbose=False)
            vehicles, emv_found = 0, False

            for r in results:
                for box in r.boxes:
                    cls = int(box.cls)
                    if cls in [2, 3, 5, 7]:  # vehicle classes
                        vehicles += 1
                    if cls == 5:  # emergency vehicle (e.g., bus/ambulance)
                        emv_found = True

                annotated = r.plot()

            # dynamically calculate timer
            base_time = 10
            factor = 2
            timer = base_time + vehicles * factor

            # update lane info
            self.lanes[lane].update(
                {
                    "vehicles": vehicles,
                    "emv_detected": emv_found,
                    "frame": annotated,
                    "timer": timer,  # ✅ dynamic allocation
                }
            )

    def get_status(self):
        return {
            lane: {
                "light": data["light"],
                "timer": data["timer"],
                "vehicles": data["vehicles"],
                "emv_detected": data["emv_detected"],
                "violators": data["violators"],
            }
            for lane, data in self.lanes.items()
        }

    def get_frame(self, lane):
        return self.lanes[lane]["frame"]


lane_videos = {
    "lane1": "videos/lane1.mp4",
    "lane2": "videos/lane2.mp4",
    "lane3": "videos/lane3.mp4",
    "lane4": "videos/lane4.mp4",
}

traffic_service = TrafficAnalyzer(lane_videos)
