from flask import Blueprint, Response, jsonify, abort
from services.traffic_analyzer import traffic_service  # ✅ import instance, not class
import cv2

traffic_bp = Blueprint("traffic", __name__)


# Get traffic status
@traffic_bp.route("/status", methods=["GET"])
def traffic_status():
    return jsonify(traffic_service.get_status())


# Generator for MJPEG stream
def gen_frames(lane):
    while True:
        frame = traffic_service.get_frame(lane)  # ✅ use instance
        if frame is None:
            continue
        ret, buffer = cv2.imencode(".jpg", frame)
        frame_bytes = buffer.tobytes()
        yield (
            b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n"
        )


# Stream endpoint
@traffic_bp.route("/stream/<lane>")
def stream(lane):
    if lane not in traffic_service.lanes:
        abort(404, description="Unknown lane")
    return Response(
        gen_frames(lane), mimetype="multipart/x-mixed-replace; boundary=frame"
    )
