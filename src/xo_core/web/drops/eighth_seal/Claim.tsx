import React from 'react';
import { Link } from 'react-router-dom';
import './Claim.css';

export const Claim: React.FC = () => {
  return (
    <div className="claim-container">
      <div className="claim-card">
        <h1 className="claim-title">
          🎉 You've Claimed the <span className="highlight">Eighth Seal</span>!
        </h1>
        <p className="claim-subtitle">
          Your <strong>NFT</strong> has been minted and is now part of your collection.
        </p>

        <div className="nft-section">
          <h2 className="nft-label">🔗 Unlock Access</h2>
          <div className="nft-badge">
            <img src="/drops/eighth_seal/assets/qr.png" alt="Your NFT QR Code" />
          </div>
          <p className="claim-note">
            ✨ Scan this QR to explore exclusive content and upcoming experiences.
          </p>
        </div>

        <Link to="/" className="claim-button">
          ⬅️ Back to Drops
        </Link>

        <footer className="claim-footer">
          🌌 Stay tuned for more surprises at <strong>xodrops.com</strong>
        </footer>
      </div>
    </div>
  );
};