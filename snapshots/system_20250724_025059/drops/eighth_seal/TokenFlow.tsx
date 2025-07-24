import React, { useEffect } from 'react';
import './TokenFlow.css';

const TokenFlow = () => {
  return (
    <div className="token-flow">
      <h2 className="token-flow-title">🧬 Token Flow Journey</h2>
      <div className="flow-diagram">
        <div className="flow-segment">
          <button
            className="flow-step animated"
            type="button"
            onClick={() => alert("Step: User")}
          >
            <div className="icon user">👤</div>
            <div className="label">User</div>
          </button>
          <div className="arrow">➡️</div>
        </div>

        <div className="flow-segment">
          <button
            className="flow-step animated"
            type="button"
            onClick={() => alert("Step: Mint")}
          >
            <div className="icon mint">🪙</div>
            <div className="label">Mint</div>
          </button>
          <div className="arrow">➡️</div>
        </div>

        <div className="flow-segment">
          <button
            className="flow-step animated"
            type="button"
            onClick={() => alert("Step: Gas (Aether)")}
          >
            <div className="icon gas">⛽</div>
            <div className="label">Gas (Aether)</div>
          </button>
          <div className="arrow">➡️</div>
        </div>

        <div className="flow-segment">
          <button
            className="flow-step animated"
            type="button"
            onClick={() => alert("Step: Claim")}
          >
            <div className="icon claim">✅</div>
            <div className="label">Claim</div>
          </button>
        </div>
      </div>
      <p className="note">
        Gas fees collected as <strong>Aether</strong>, optionally <strong>ETH</strong> if hybrid path is enabled.
      </p>
    </div>
  );
};

export default TokenFlow;