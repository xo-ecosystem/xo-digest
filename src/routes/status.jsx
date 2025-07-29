import React, { useEffect, useState } from 'react';

const DeployStatus = () => {
  const [status, setStatus] = useState([]);
  const [filter, setFilter] = useState('all');
  const [expanded, setExpanded] = useState({});
  const [logLevel, setLogLevel] = useState('all');

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const res = await fetch('/.deploy-log.json');
        const data = await res.json();
        setStatus(data);
      } catch (err) {
        console.error('Failed to fetch deploy log:', err);
      }
    };

    fetchStatus();
    const interval = setInterval(fetchStatus, 5000);
    return () => clearInterval(interval);
  }, []);

  const getStatusColor = (status) => {
    if (status === 'success') return 'green';
    if (status === 'failed') return 'red';
    return 'gray';
  };

  const toggleExpanded = (idx) => {
    setExpanded((prev) => ({ ...prev, [idx]: !prev[idx] }));
  };

  const uniqueServices = Array.from(new Set(status.map(s => s.service)));

  const filtered = status
    .filter(entry =>
      (filter === 'all' || entry.service === filter) &&
      (logLevel === 'all' || entry.status === logLevel)
    )
    .sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));

  return (
    <div style={{ padding: '1rem' }}>
      <h2>📦 Live Deploy Status</h2>

      <div style={{ marginBottom: '1rem' }}>
        <label>🔍 Filter by Service: </label>
        <select value={filter} onChange={(e) => setFilter(e.target.value)}>
          <option value="all">All</option>
          {uniqueServices.map((svc) => (
            <option key={svc} value={svc}>{svc}</option>
          ))}
        </select>
      </div>

      <div style={{ marginBottom: '1rem' }}>
        <label>⚠️ Filter by Log Level: </label>
        <select value={logLevel} onChange={(e) => setLogLevel(e.target.value)}>
          <option value="all">All</option>
          <option value="success">Success</option>
          <option value="failed">Failed</option>
        </select>
      </div>

      <ul>
        {filtered.map((entry, idx) => (
          <li
            key={idx}
            style={{
              marginBottom: '0.75rem',
              borderLeft: `4px solid ${getStatusColor(entry.status)}`,
              paddingLeft: '0.75rem'
            }}
          >
            <strong>{entry.service}</strong> – <span style={{ color: getStatusColor(entry.status) }}>{entry.status}</span> <br />
            <small>{entry.timestamp}</small>
            {entry.dns && (
              <div style={{ fontSize: '0.85rem', marginTop: '0.25rem' }}>
                🌐 DNS: {entry.dns.valid ? '✅ Valid' : '❌ Invalid'}
              </div>
            )}
            <div style={{ fontSize: '0.8rem', color: '#666', marginTop: '0.5rem' }}>
              <button onClick={() => toggleExpanded(idx)} style={{ fontSize: '0.75rem' }}>
                {expanded[idx] ? '🔽 Hide Log' : '▶ Show Log'}
              </button>
              {expanded[idx] && (
                <pre style={{ fontSize: '0.75rem', marginTop: '0.5rem', background: '#f9f9f9', padding: '0.5rem' }}>
                  {JSON.stringify(entry, null, 2)}
                </pre>
              )}
              <div style={{ marginTop: '0.5rem' }}>
                <iframe
                  src="/dns-history-chart.html"
                  title="DNS Chart"
                  style={{ width: '100%', height: '250px', border: 'none' }}
                />
              </div>
            </div>
          </li>
        ))}
      </ul>
      
      <button
        onClick={() => {
          const blob = new Blob([JSON.stringify(filtered, null, 2)], { type: 'application/json' });
          const url = URL.createObjectURL(blob);
          const a = document.createElement('a');
          a.href = url;
          a.download = 'deploy-log-export.json';
          a.click();
        }}
        style={{ marginTop: '1rem' }}
      >
        ⬇️ Export Filtered Logs
      </button>
    </div>
  );
};

export default DeployStatus; 