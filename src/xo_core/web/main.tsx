import { createRoot } from 'react-dom/client';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Drop } from './drops/eighth_seal/Drop';
import { Claim } from './drops/eighth_seal/Claim'; // scaffolded screen
import { Explorer } from './explorer/Explorer'; // new explorer component

const App = () => (
  <BrowserRouter>
    <Routes>
      <Route path="/drops/eighth_seal" element={<Drop />} />
      <Route path="/drops/eighth_seal/claim" element={<Claim />} />
      <Route path="/explorer/:slug" element={<Explorer />} />
    </Routes>
  </BrowserRouter>
);

const container = document.getElementById('root')!;
const root = createRoot(container);
root.render(<App />);