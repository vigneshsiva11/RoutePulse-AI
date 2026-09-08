import React, { useState, useEffect, useCallback } from "react";
import Header from "../components/Header";
import TrafficLight from "../components/TrafficLight";
import ViolatorTable from "../components/ViolatorTable";
import AnalyticsChart from "../components/AnalyticsChart";
import EmergencyAlert from "../components/EmergencyAlert";

const LANE_ORDER = ["lane1", "lane2", "lane3", "lane4"];

function Dashboard() {
  const [lanes, setLanes] = useState({});
  const [violators, setViolators] = useState([]);
  const [emv, setEmv] = useState(null);
  // The backend signal controller, not the UI, chooses the green lane.
  const activeLane = Object.entries(lanes).find(([, lane]) => lane.light === "green")?.[0] ?? null;

  const fetchData = useCallback(async () => {
    try {
      const response = await fetch("http://localhost:5000/traffic/status");
      if (!response.ok) throw new Error(`Status request failed (${response.status})`);
      const data = await response.json();
      setLanes(data);
      setViolators(Object.entries(data).flatMap(([lane, value]) => (value.violators || []).map((item) => ({ ...item, lane }))));
      const emergencyLane = Object.entries(data).find(([, value]) => value.emv_detected);
      setEmv(emergencyLane ? { lane: emergencyLane[0], confidence: emergencyLane[1].emergency_confidence } : null);
    } catch (error) {
      console.error("Error fetching traffic status:", error);
    }
  }, []);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 1000);
    return () => clearInterval(interval);
  }, [fetchData]);

  return (
    <div className="min-h-screen bg-gray-100 p-6">
      <Header stcEnabled={true} toggleSTC={() => {}} team={[]} />
      {emv && <EmergencyAlert message={`Ambulance confirmed in ${emv.lane} (${Math.round(emv.confidence * 100)}%)`} emphasize />}
      <div className="grid grid-cols-2 gap-6 mt-4">
        <div className="grid grid-cols-2 gap-4">
          {LANE_ORDER.map((lane) => (
            <div key={lane} className={`rounded-xl overflow-hidden relative ${activeLane === lane ? "ring-4 ring-green-400" : ""}`}>
              <img src={`http://localhost:5000/traffic/stream/${lane}`} alt={lane} className="w-full h-48 object-cover" />
              <div className="absolute bottom-0 w-full bg-black/60 text-white text-xs p-1 text-center">{lane.toUpperCase()}</div>
            </div>
          ))}
        </div>
        <div className="bg-white rounded-2xl shadow p-4">
          <h3 className="text-lg font-semibold mb-4 text-center">Traffic Control Panel</h3>
          <div className="grid grid-cols-2 gap-6">
            {LANE_ORDER.map((lane) => {
              const state = lanes[lane];
              const green = state?.light === "green";
              return <div key={lane} className="flex flex-col items-center bg-gray-50 rounded-lg p-3 shadow-sm">
                <TrafficLight color={state?.light || "red"} timer={green ? state?.timer || 0 : 0} />
                <div className="mt-2 font-medium">{lane.toUpperCase()}</div>
                <div className="text-xs text-gray-500">Vehicles: {state?.vehicles || 0}</div>
                {state?.emv_detected && <div className="text-xs text-red-600 font-semibold">Ambulance priority</div>}
                <div className="text-xs text-gray-400">Pedestrian: {green ? <span className="text-red-600 font-semibold">Stop</span> : <span className="text-green-600 font-semibold">Walk</span>}</div>
              </div>;
            })}
          </div>
        </div>
      </div>
      <div className="grid grid-cols-2 gap-6 mt-6">
        <ViolatorTable violators={violators} />
        <AnalyticsChart lanesData={Object.fromEntries(Object.entries(lanes).map(([key, value]) => [key, { count: value.vehicles }]))} />
      </div>
    </div>
  );
}

export default Dashboard;
