from flask import Blueprint, request, jsonify
from services.traffic_analyzer import traffic_service

control_bp = Blueprint("control_bp", __name__)

# Get traffic light status
@control_bp.route("/status", methods=["GET"])
def get_status():
    status = traffic_service.get_status()
    return jsonify(status)


# Manually change traffic light for a lane
@control_bp.route("/change-light", methods=["POST"])
def change_light():
    data = request.json
    lane = data.get("lane")
    state = data.get("state")  # red/green/yellow
    result = traffic_service.update_light(lane, state)
    return jsonify({"message": result})


# Enable / Disable Smart Traffic Control
@control_bp.route("/stc-toggle", methods=["POST"])
def stc_toggle():
    data = request.json
    enable = data.get("enable", True)
    result = traffic_service.toggle_stc(enable)
    return jsonify({"stc_enabled": result})
