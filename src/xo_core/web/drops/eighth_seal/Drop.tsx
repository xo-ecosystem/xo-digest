import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import yaml from 'js-yaml';
import './styles.css';
import { ScrollFX } from './ScrollFX';
import GameTraitsViewer from '../../components/GameTraitsViewer';
import { getDropTraits } from '../../traits/api';
import type { Trait } from '../../types/traits';

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
  const [traits, setTraits] = useState<Trait[]>([]);
  const navigate = useNavigate();

  useEffect(() => {
    fetch('/drops/eighth_seal/data.coin.yml')
      .then(res => res.text())
      .then(yaml.load)
      .then((loadedData) => setData(loadedData as DropData))
      .catch((err) => setError(`❌ Failed to load drop data: ${err.message}`));
  }, []);

  useEffect(() => {
    getDropTraits('eighth_seal_3d').then(setTraits).catch(() => setTraits([]));
  }, []);

  if (error) return <div className="text-red-600 p-4 text-center font-medium">{error}</div>;
  if (!data) return <div className="text-gray-500 p-4 text-center">⏳ Loading drop data...</div>;

  const imageUrl = useDynamicImage && data.image ? data.image : '/drops/eighth_seal/assets/qr.png';

  const hasGlow = traits.some(t => (t.game_effects?.unity_webgl as any)?.glow);

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

      <div className="mt-6 space-y-3">
        {hasGlow && (
          <div>
            <a href="/three-glow-demo" className="inline-flex items-center gap-2 px-3 py-1 rounded bg-yellow-100 text-yellow-800">
              ✨ Glow-Ready — View Demo
            </a>
          </div>
        )}
        <GameTraitsViewer traits={traits} />
      </div>
    </div>
  );
};

"""
xo_core.vault
Lazy import facade to avoid circular imports between vault submodules
when tests/tasks import from xo_core.vault.* during collection.

Do NOT perform any eager intra-package imports at module import time.
"""

from typing import Any

__all__ = [
    # modules exposed lazily
    "unseal",
    "bootstrap",
    "api",
    "utils",
    # function passthroughs commonly imported from package root
    "sign_all",
    "get_vault_client",
]

def __getattr__(name: str) -> Any:
    if name == "unseal":
        from . import unseal as m
        return m
    if name == "bootstrap":
        from . import bootstrap as m
        return m
    if name == "api":
        from . import api as m
        return m
    if name == "utils":
        from . import utils as m
        return m
    raise AttributeError(f"module 'xo_core.vault' has no attribute {name!r}")

def sign_all(*args, **kwargs):
    # Defer to implementation in .api (or update if moved)
    from .api import sign_all as _sign_all  # type: ignore
    return _sign_all(*args, **kwargs)

def get_vault_client(*args, **kwargs):
    # Defer to implementation in .bootstrap (or update if moved)
    from .bootstrap import get_vault_client as _get_vault_client  # type: ignore
    return _get_vault_client(*args, **kwargs)
