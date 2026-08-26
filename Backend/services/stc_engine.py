def decide_signal(ai_result):
    if ai_result["emergency_detected"]:
        return {"priority_lane": "EmergencyLane", "status": "GREEN"}

    # simple prototype logic → give priority to lane with most vehicles
    lane_counts = {
        "lane1": ai_result["vehicles"],
        "lane2": ai_result["vehicles"] // 2,
        "lane3": ai_result["vehicles"] // 3,
    }
    priority = max(lane_counts, key=lane_counts.get)

    return {"priority_lane": priority, "status": "GREEN"}
