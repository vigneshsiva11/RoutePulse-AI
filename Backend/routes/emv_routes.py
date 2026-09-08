from flask import Blueprint, jsonify
from services.traffic_analyzer import traffic_service

emv_bp = Blueprint("emv_bp", __name__)
# Check if EMV is detected
@emv_bp.route("/emv-status", methods=["GET"])
def emv_status():
    lanes = traffic_service.check_emv()
    return jsonify({"emv_detected": bool(lanes), "lanes": lanes})


# Clear lane for EMV
@emv_bp.route("/clear-emv", methods=["POST"])
def clear_emv():
    return jsonify({"priority_lane": traffic_service.clear_for_emv()})
