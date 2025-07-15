import React from 'react';
import './Claim.css';

const Claim = () => {
  return (
    <div className="claim-container">
      <div className="claim-card">
        <h1>🌟 Token Claimed!</h1>
        <p className="claim-message">
          You’ve successfully minted your digital collectible.
          It’s now part of your wallet and history.
        </p>
        <div className="claim-actions">
          <a href="/" className="claim-button">🏠 Back to Home</a>
          <a href="/drops/eighth_seal" className="claim-button secondary">🔁 View Drop</a>
        </div>
        <div className="claim-badge">
          <img src="/drops/eighth_seal/assets/qr.png" alt="Claim QR" />
          <p className="qr-caption">Scan to view or share your token</p>
        </div>
      </div>
    </div>
  );
};

export default Claim;