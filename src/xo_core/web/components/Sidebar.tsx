import React from 'react';
import { Link } from 'react-router-dom';

export const Sidebar = () => (
  <nav style={{ padding: '1rem', borderRight: '1px solid #ccc' }}>
    <ul style={{ listStyle: 'none', padding: 0 }}>
      <li><Link to="/vault">Vault</Link></li>
      <li><Link to="/drops/eighth_seal">Drop</Link></li>
      <li><Link to="/drops/eighth_seal/claim">Claim</Link></li>
      <li><Link to="/explorer/example">Explorer</Link></li>
      <li><Link to="/digest">Digest</Link></li>
    </ul>
  </nav>
);
