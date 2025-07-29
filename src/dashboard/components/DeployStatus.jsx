import React, { useEffect, useState } from 'react';

const DeployStatus = () => {
  const [status, setStatus] = useState(null);

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const res = await fetch('/logs/.deploy-log.json');
        const data = await res.json();
        setStatus(data);
      } catch (err) {
        console.error('Failed to load deploy status:', err);
      }
    };

    fetchStatus();
    const interval = setInterval(fetchStatus, 10000); // refresh every 10s
    return () => clearInterval(interval);
  }, []);

  if (!status) return <div>Loading...</div>;

  return (
    <div>
      <h2>📦 Deploy Status</h2>
      <ul>
        {status.map((entry, idx) => (
          <li key={idx}>
            <strong>{entry.service}</strong> – {entry.status} @ {entry.timestamp}
          </li>
        ))}
      </ul>
    </div>
  );
};

export default DeployStatus;
