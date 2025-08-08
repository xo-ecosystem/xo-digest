import React from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Drop } from './drops/eighth_seal/Drop';
import { Claim } from './drops/eighth_seal/Claim'; // scaffolded screen
import TraitExplorer from './pages/TraitExplorer';
import ThreeGlowDemo from './pages/ThreeGlowDemo';
import { VaultDashboard } from './vault/VaultDashboard'; // vault dashboard
import { Sidebar } from './components/Sidebar';
import { NotFound } from './pages/NotFound';

const App = () => (
  <BrowserRouter>
    <div style={{ display: 'flex' }}>
      <Sidebar />
      <div style={{ flex: 1, padding: '1rem' }}>
        <Routes>
          <Route path="/" element={<VaultDashboard />} />
          <Route path="/vault" element={<VaultDashboard />} />
          <Route path="/drops/eighth_seal" element={<Drop />} />
          <Route path="/drops/eighth_seal/claim" element={<Claim />} />
          <Route path="/traits" element={<TraitExplorer />} />
          <Route path="/three-glow-demo" element={<ThreeGlowDemo dropId="eighth_seal_3d" />} />
          <Route path="/digest" element={<h2>Digest Viewer Placeholder</h2>} />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </div>
    </div>
  </BrowserRouter>
);

const container = document.getElementById('root')!;
const root = createRoot(container);
root.render(<App />);