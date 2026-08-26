import React, { useState, useEffect, useCallback } from "react";
import Header from "../components/Header";
import TrafficLight from "../components/TrafficLight";
import ViolatorTable from "../components/ViolatorTable";
import AnalyticsChart from "../components/AnalyticsChart";
import EmergencyAlert from "../components/EmergencyAlert";

const LANE_ORDER = ["lane1", "lane2", "lane3", "lane4"]; // backend keys

function Dashboard() {
  const [lanes, setLanes] = useState({});
  const [violators, setViolators] = useState([]);
  const [emv, setEmv] = useState(null);

  const [activeLane, setActiveLane] = useState(null);
  const [timer, setTimer] = useState(15);

  // reusable fetch function
  const fetchData = useCallback(async () => {
    try {
      const res = await fetch("http://localhost:5000/traffic/status");
      const data = await res.json();
      setLanes(data);

      // flatten violators
      setViolators(
        Object.entries(data).flatMap(([lane, d]) =>
          d.violators.map((v) => ({ ...v, lane }))
        )
      );

      // detect EMV
      const emvLane = Object.entries(data).find(
        ([_, d]) => d.emv_detected
      );
      if (emvLane) {
        setEmv({ lane: emvLane[0], type: "Emergency Vehicle" });
      } else {
        setEmv(null);
      }

      // if no active lane → pick lane with most vehicles
      if (!activeLane) {
        const laneWithMostVehicles = Object.entries(data).reduce(
          (max, [lane, d]) =>
            d.vehicles > (max?.vehicles || 0)
              ? { lane, vehicles: d.vehicles }
              : max,
          null
        );
        if (laneWithMostVehicles) {
          setActiveLane(laneWithMostVehicles.lane);
          setTimer(15); // reset timer
        }
      }
    } catch (err) {
      console.error("Error fetching status:", err);
    }
  }, [activeLane]);

  // periodic fetch
  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 2000);
    return () => clearInterval(interval);
  }, [fetchData]);

  // countdown logic
  useEffect(() => {
    if (!activeLane) return;

    const countdown = setInterval(() => {
      setTimer((t) => {
        if (t <= 1) {
          // when timer ends → pick next lane with highest vehicles
          const laneWithMostVehicles = Object.entries(lanes).reduce(
            (max, [lane, d]) =>
              d.vehicles > (max?.vehicles || 0)
                ? { lane, vehicles: d.vehicles }
                : max,
            null
          );

          if (laneWithMostVehicles) {
            setActiveLane(laneWithMostVehicles.lane);
            fetchData(); //  refresh vehicle counts immediately
            return 15; // reset timer
          }
        }
        return t - 1;
      });
    }, 1000);

    return () => clearInterval(countdown);
  }, [lanes, activeLane, fetchData]);

  return (
    <div className="min-h-screen bg-gray-100 p-6">
      {/* Header */}
      <Header stcEnabled={true} toggleSTC={() => { }} team={[]} />

      {/* Emergency Alert */}
      {emv && (
        <EmergencyAlert
          message={`${emv.type} in ${emv.lane}`}
          emphasize
        />
      )}

      <div className="grid grid-cols-2 gap-6 mt-4">
        {/* Left Side → Video Feeds */}
        <div className="grid grid-cols-2 gap-4">
          {LANE_ORDER.map((lane) => (
            <div
              key={lane}
              className={`rounded-xl overflow-hidden relative ${activeLane === lane ? "ring-4 ring-green-400" : ""
                }`}
            >
              <img
                src={`http://localhost:5000/traffic/stream/${lane}`}
                alt={lane}
                className="w-full h-48 object-cover"
              />
              <div className="absolute bottom-0 w-full bg-black/60 text-white text-xs p-1 text-center">
                {lane.toUpperCase()}
              </div>
            </div>
          ))}
        </div>

        {/* Right Side → Control Panel */}
        <div className="bg-white rounded-2xl shadow p-4">
          <h3 className="text-lg font-semibold mb-4 text-center">
            Traffic Control Panel
          </h3>

          <div className="grid grid-cols-2 gap-6">
            {LANE_ORDER.map((lane) => (
              <div
                key={lane}
                className="flex flex-col items-center bg-gray-50 rounded-lg p-3 shadow-sm"
              >
                <TrafficLight
                  color={activeLane === lane ? "green" : "red"}
                  timer={activeLane === lane ? timer : 0}
                />
                <div className="mt-2 font-medium">{lane.toUpperCase()}</div>
                <div className="text-xs text-gray-500">
                  Vehicles: {lanes[lane]?.vehicles || 0}
                </div>
                <div className="text-xs text-gray-400">
                  Pedestrian:{" "}
                  {activeLane === lane ? (
                    <span className="text-red-600 font-semibold">Stop</span>
                  ) : (
                    <span className="text-green-600 font-semibold">Walk</span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Bottom Section */}
      <div className="grid grid-cols-2 gap-6 mt-6">
        <ViolatorTable violators={violators} />
        <AnalyticsChart
          lanesData={Object.fromEntries(
            Object.entries(lanes).map(([k, v]) => [k, { count: v.vehicles }])
          )}
        />
      </div>
    </div>
  );
}

export default Dashboard;
