import React from "react";

function Header({ stcEnabled, toggleSTC, team }) {
  return (
    <header className="flex items-center justify-center bg-white rounded-2xl p-4 shadow">
      <h1 className="text-xl font-bold mx-auto">TRAFFIX</h1>
    </header>
  );
}

export default Header;
