import React from "react";

export const Badge: React.FC<{ label: string }> = ({ label }) => {
  return (
    <div
      className="inline-flex items-center px-3 py-1 text-sm font-semibold text-white bg-gradient-to-r from-indigo-600 to-fuchsia-600 rounded-full shadow-lg animate-pulse transition-transform duration-200 hover:scale-105 focus-visible:ring-2 focus-visible:ring-white focus:outline-none"
      role="status"
      aria-label={label}
      title={label}
    >
      <span className="sr-only">Status: </span>
      {label}
    </div>
  );
};

export default Badge;