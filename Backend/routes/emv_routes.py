from flask import Blueprint, jsonify
from services.traffic_analyzer import TrafficAnalyzer

emv_bp = Blueprint("emv_bp", __name__)
lane_videos = {
    "lane1": "videos/lane1.mp4",
    "lane2": "videos/lane2.mp4",
    "lane3": "videos/lane3.mp4",
    "lane4": "videos/lane4.mp4",
}

# Shared TrafficAnalyzer instance
traffic_service = TrafficAnalyzer(lane_videos)


# Check if EMV is detected
@emv_bp.route("/emv-status", methods=["GET"])
def emv_status():
    emv_detected = traffic_service.check_emv()
    return jsonify({"emv_detected": emv_detected})


# Clear lane for EMV
@emv_bp.route("/clear-emv", methods=["POST"])
def clear_emv():
    result = traffic_service.clear_for_emv()
    return jsonify({"message": result})
