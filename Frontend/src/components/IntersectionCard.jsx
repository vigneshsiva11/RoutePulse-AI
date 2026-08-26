import React from "react";
import TrafficLight from "./TrafficLight";

const laneNames = ["North", "East", "South", "West"];

function IntersectionCard({ id, state }) {
  return (
    <div className="bg-white rounded-2xl shadow p-4 flex flex-col gap-3">
      <h3 className="text-lg font-semibold">{id}</h3>

      <div className="grid grid-cols-2 gap-3">
        {laneNames.map((ln) => (
          <div
            key={ln}
            className="bg-gray-50 rounded-lg p-3 flex items-center gap-3"
          >
            <TrafficLight color={state.lanes[ln].signal} small />
            <div>
              <div className="text-sm font-medium">{ln}</div>
              <div className="text-xs text-gray-500">
                Vehicles: {state.lanes[ln].count}
              </div>
              <div className="text-xs text-gray-400">
                Priority: {state.lanes[ln].priority}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default IntersectionCard;
