import React from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from "recharts";

const laneNames = ["North", "East", "South", "West"];


function AnalyticsChart({ lanesData = []}) {
  const data = laneNames.map((ln) => ({
    name: ln,
    count: lanesData[ln]?.count || 0,
  }));

  return (
    <div className="bg-white rounded-2xl shadow p-4 h-full">
      <h4 className="font-semibold mb-3">Traffic Intensity</h4>
      <div style={{ width: "100%", height: 220 }}>
        <ResponsiveContainer>
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis />
            <Tooltip />
            <Line
              type="monotone"
              dataKey="count"
              stroke="#3b82f6"
              strokeWidth={3}
              dot={{ r: 5, fill: "#3b82f6" }}
              activeDot={{ r: 7 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

export default AnalyticsChart;
