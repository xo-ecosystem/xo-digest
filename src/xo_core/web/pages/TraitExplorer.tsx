import React, { useEffect, useMemo, useState } from 'react';
import { getAllTraits } from '../traits/api';
import type { Trait } from '../types/traits';
import GameTraitsViewer from '../components/GameTraitsViewer';

export const TraitExplorer: React.FC = () => {
  const [allByDrop, setAllByDrop] = useState<Record<string, Trait[]>>({});
  const [query, setQuery] = useState('');
  const [platform, setPlatform] = useState<string>('');
  const [rarity, setRarity] = useState<string>('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getAllTraits()
      .then((data) => setAllByDrop(data))
      .catch((err) => setError(`Failed to load traits: ${err?.message || err}`))
      .finally(() => setLoading(false));
  }, []);

  const filtered: Trait[] = useMemo(() => {
    const list = Object.values(allByDrop).flat();
    return list.filter((t) => {
      const matchesQuery = !query ||
        t.name.toLowerCase().includes(query.toLowerCase()) ||
        t.description?.toLowerCase().includes(query.toLowerCase()) ||
        (t.tags || []).some((tag) => tag.toLowerCase().includes(query.toLowerCase()));

      const matchesRarity = !rarity || (t.rarity || '').toLowerCase() === rarity.toLowerCase();

      const matchesPlatform = !platform ||
        (t.game_effects && Object.prototype.hasOwnProperty.call(t.game_effects, platform));

      return matchesQuery && matchesRarity && matchesPlatform;
    });
  }, [allByDrop, query, platform, rarity]);

  if (loading) return <div>Loading traits…</div>;
  if (error) return <div className="text-red-600">{error}</div>;

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">Trait Explorer</h1>
      <div className="flex gap-2 items-center flex-wrap">
        <input
          placeholder="Search by name, tag, description"
          className="border px-2 py-1 rounded"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <select className="border px-2 py-1 rounded" value={platform} onChange={(e) => setPlatform(e.target.value)}>
          <option value="">All Platforms</option>
          <option value="minecraft">Minecraft</option>
          <option value="sims">Sims</option>
          <option value="unity_webgl">Unity WebGL</option>
          <option value="vrchat">VRChat</option>
        </select>
        <select className="border px-2 py-1 rounded" value={rarity} onChange={(e) => setRarity(e.target.value)}>
          <option value="">All Rarities</option>
          <option value="common">Common</option>
          <option value="uncommon">Uncommon</option>
          <option value="rare">Rare</option>
          <option value="epic">Epic</option>
          <option value="legendary">Legendary</option>
        </select>
      </div>
      <GameTraitsViewer traits={filtered} />
    </div>
  );
};

export default TraitExplorer;


