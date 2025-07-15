import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import yaml from 'js-yaml';
import './styles.css'; // assumes Tailwind CSS is extended with custom animation if needed
import { ScrollFX } from './ScrollFX';

interface DropData {
  title: string;
  description: string;
  image?: string;
  mint_url?: string;
  [key: string]: any;
}

export const Drop = () => {
  const [data, setData] = useState<DropData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [useDynamicImage, setUseDynamicImage] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    fetch('/drops/eighth_seal/data.coin.yml')
      .then(res => res.text())
      .then(yaml.load)
      .then((loadedData) => setData(loadedData as DropData))
      .catch((err) => setError(`❌ Failed to load drop data: ${err.message}`));
  }, []);

  if (error) return <div className="text-red-600 p-4 text-center font-medium">{error}</div>;
  if (!data) return <div className="text-gray-500 p-4 text-center">⏳ Loading drop data...</div>;

  const imageUrl = useDynamicImage && data.image ? data.image : '/drops/eighth_seal/assets/qr.png';

  return (
    <div className="max-w-2xl mx-auto p-6 border rounded-2xl shadow-md bg-white space-y-6 animate-fade-in">
      <ScrollFX />
      <div className="text-center space-y-2">
        <h1 className="text-4xl font-extrabold tracking-tight text-gray-900 animate-fade-in delay-100">
          {data.title}
        </h1>
        <p className="text-lg text-gray-600 leading-relaxed animate-fade-in delay-200">
          {data.description}
        </p>
      </div>

      <div className="relative animate-fade-in delay-300">
        <div className="flex justify-center mb-4 animate-pulse">
          <div className="w-8 h-8 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full blur-sm opacity-70 animate-spin-slow"></div>
        </div>
        <img
          src={imageUrl}
          alt={data?.title || 'Drop image'}
          className="rounded-xl shadow-lg mx-auto w-full max-w-md"
        />
        <button
          onClick={() => setUseDynamicImage(!useDynamicImage)}
          className="absolute top-2 right-2 bg-white bg-opacity-80 text-xs px-2 py-1 rounded shadow hover:bg-opacity-100"
        >
          {useDynamicImage ? 'Use fallback image' : 'Use dynamic image'}
        </button>
      </div>

      {data.mint_url && (
        <div className="text-center animate-fade-in delay-500">
          <button
            onClick={() => {
              window.open(data.mint_url, '_blank');
              setTimeout(() => navigate('/drops/eighth_seal/claim'), 3000);
            }}
            className="inline-block bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-3 px-6 rounded-lg shadow transition duration-300"
          >
            🚀 Mint Now
          </button>
        </div>
      )}

      <div className="bg-gray-100 p-4 rounded-lg text-sm overflow-x-auto animate-fade-in delay-700">
        <pre className="whitespace-pre-wrap font-mono text-gray-700">
          {JSON.stringify(data, null, 2)}
        </pre>
      </div>
    </div>
  );
};