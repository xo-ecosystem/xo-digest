import React, { useState, useEffect } from 'react';

type Variant = {
  name: string;
  image: string;
  description: string;
  price?: string;
};

const variants: Variant[] = [
  {
    name: 'Aether Scroll',
    image: '/drops/aether_mint/aether_scroll.png',
    description: 'The first whisper of the eighth seal.',
    price: '0.01 ETH'
  }
];

export default function Drop() {
  const [selected, setSelected] = useState(0);
  const [minted, setMinted] = useState(false);
  const variant = variants[selected];

  const handleMint = () => {
    // Simulate mint logic (replace with actual Thirdweb or smart contract call)
    console.log(`Minting ${variant.name} for ${variant.price}`);
    setMinted(true);
  };

  useEffect(() => {
    if (minted) {
      // This effect triggers the visual effect when minted is true
    }
  }, [minted]);

  return (
    <main className="drop-container" style={{ position: 'relative' }}>
      <h1>🌌 {variant.name}</h1>
      <img src={variant.image} alt={variant.name} className="drop-image" />
      <p>{variant.description}</p>
      {variant.price && <p>Price: {variant.price}</p>}
      {!minted ? (
        <button className="mint-button" onClick={handleMint}>🔓 Mint</button>
      ) : (
        <p>✅ Successfully minted!</p>
      )}
      {minted && <div className="xo-lightning" />}
      <style jsx>{`
        .xo-lightning {
          position: absolute;
          top: 50%;
          left: 50%;
          width: 240px;
          height: 240px;
          background: radial-gradient(circle, rgba(255, 255, 255, 0.2), transparent 70%);
          transform: translate(-50%, -50%);
          border-radius: 50%;
          animation: xoFlash 3s ease-out forwards;
          pointer-events: none;
          z-index: 10;
          box-shadow: 0 0 40px 10px rgba(173, 216, 230, 0.4);
        }

        @keyframes xoFlash {
          0% {
            opacity: 0;
            transform: scale(0.8) translate(-50%, -50%);
          }
          25% {
            opacity: 1;
            transform: scale(1.05) translate(-50%, -50%);
          }
          75% {
            opacity: 0.7;
            transform: scale(1.1) translate(-50%, -50%);
          }
          100% {
            opacity: 0;
            transform: scale(1.2) translate(-50%, -50%);
          }
        }
      `}</style>
    </main>
  );
}