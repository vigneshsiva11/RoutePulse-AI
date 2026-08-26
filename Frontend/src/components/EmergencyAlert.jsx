import React from "react";

export default function EmergencyAlert({ title = "Emergency Vehicle Detected", message = "", emphasize = false }) {
  return (
    <div className={`w-full rounded-md p-3 text-sm ${emphasize ? "bg-red-100 border border-red-300" : "bg-yellow-50 border border-yellow-200"}`}>
      <div className="flex items-center gap-3">
        <div className="w-3 h-3 rounded-full bg-red-500 shadow" />
        <div className="font-medium text-red-700">{title}</div>
      </div>
      {message && <div className="mt-1 text-xs text-red-600">{message}</div>}
      <div className="text-xs text-gray-500 mt-1">Auto preemption active</div>
    </div>
  );
}
