import React, { useEffect, useState } from "react";
import Timer from "../assets/Timer";

function TrafficLight({ color = "red", timer = 10, small = false }) {
  const [timeLeft, setTimeLeft] = useState(timer);

  useEffect(() => {
    setTimeLeft(timer); // reset when prop changes
  }, [timer]);

  useEffect(() => {
    if (timeLeft <= 0) return;
    const interval = setInterval(() => {
      setTimeLeft((t) => t - 1);
    }, 1000);
    return () => clearInterval(interval);
  }, [timeLeft]);

  const lightClass = (c) => {
    const base =
      "w-12 h-12 rounded-full flex items-center justify-center border-2 border-gray-800";
    if (c === color) {
      return `${base} text-white ${
        c === "red"
          ? "bg-red-600 shadow-[0_0_25px_rgba(255,0,0,0.9)]"
          : c === "yellow"
          ? "bg-yellow-400 shadow-[0_0_25px_rgba(255,255,0,0.9)]"
          : "bg-green-500 shadow-[0_0_25px_rgba(0,255,0,0.9)]"
      }`;
    }
    return `${base} bg-gray-900`;
  };

  return (
    <div className="flex flex-col items-center">
      {/* Light casing */}
      <div className="bg-gray-800 rounded-2xl p-3 flex flex-col gap-3 shadow-lg">
        <div className={lightClass("red")}></div>
        <div className={lightClass("yellow")}></div>
        <div className={lightClass("green")}></div>
      </div>

      {/* Timer with ticking clock */}
      <div className="mt-2 flex flex-col items-center">
        <div className="relative w-10 h-10 rounded-full border-2 border-gray-700 flex items-center justify-center text-sm font-bold">
          {timeLeft}
          <div
            className="absolute w-full h-full rounded-full border-2 border-green-600 border-t-transparent animate-spin-slow"
            style={{ animationDuration: "60s" }}
          ></div>
        </div>
        <span className="text-xs text-gray-600 mt-1">
          <Timer />
        </span>
      </div>
    </div>
  );
}

export default TrafficLight;
