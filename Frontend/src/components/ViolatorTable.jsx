import React from "react";

function ViolatorTable({ violators }) {
  return (
    <div className="bg-white rounded-2xl shadow p-4">
      <h4 className="font-semibold mb-3">Violators</h4>
      {violators.length === 0 ? (
        <div className="text-sm text-gray-500">No violators detected</div>
      ) : (
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left text-xs text-gray-500">
              <th>Plate</th>
              <th>Lane</th>
              <th>Time</th>
              <th>Fine</th>
            </tr>
          </thead>
          <tbody>
            {violators.map((v, i) => (
              <tr key={i} className="border-t">
                <td className="py-2">{v.plate}</td>
                <td className="py-2">{v.lane}</td>
                <td className="py-2">{v.time}</td>
                <td className="py-2">₹{v.fine}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

export default ViolatorTable;
