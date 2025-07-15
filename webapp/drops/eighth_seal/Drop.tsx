import React, { useState } from 'react';
import coin from './coin.yml';
import qr from './assets/qr.png';

const Drop: React.FC = () => {
  const [useFallback, setUseFallback] = useState(false);

  const {
    title = 'Eighth Seal Drop',
    description = 'An exclusive collectible scroll.',
    image,
    mint_url,
    metadata = {}
  } = coin || {};

  const displayedImage = useFallback ? qr : (image ?? qr);

  return (
    <div style={{ padding: '2rem', fontFamily: 'Inter, sans-serif', maxWidth: '600px', margin: 'auto' }}>
      <h1 style={{ fontSize: '2rem', marginBottom: '1rem' }}>{title}</h1>
      <p style={{ fontSize: '1.1rem', marginBottom: '1.5rem' }}>{description}</p>
      <img
        src={displayedImage}
        alt="Drop Preview"
        style={{ maxWidth: '100%', borderRadius: '8px', marginBottom: '1rem' }}
      />
      <button
        onClick={() => setUseFallback(!useFallback)}
        style={{
          marginBottom: '1rem',
          padding: '0.5rem 1rem',
          fontSize: '0.9rem',
          borderRadius: '4px',
          border: '1px solid #ccc',
          cursor: 'pointer'
        }}
      >
        Toggle QR Preview
      </button>
      <ul style={{ listStyle: 'none', padding: 0, fontSize: '0.95rem', marginBottom: '1.5rem' }}>
        {metadata.edition && <li><strong>Edition:</strong> {metadata.edition}</li>}
        {metadata.supply && <li><strong>Supply:</strong> {metadata.supply}</li>}
        {metadata.tags && <li><strong>Tags:</strong> {metadata.tags.join(', ')}</li>}
      </ul>
      {mint_url && (
        <a
          href={mint_url}
          target="_blank"
          rel="noreferrer"
          style={{
            display: 'inline-block',
            padding: '0.75rem 1.25rem',
            backgroundColor: '#111',
            color: '#fff',
            textDecoration: 'none',
            borderRadius: '4px',
            fontWeight: 'bold'
          }}
        >
          Mint Now
        </a>
      )}
    </div>
  );
};

export default Drop;
