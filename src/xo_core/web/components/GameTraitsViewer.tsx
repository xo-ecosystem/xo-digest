import React from 'react';
import type { Trait } from '../types/traits';

type Props = { traits: Trait[] };

export const GameTraitsViewer: React.FC<Props> = ({ traits }) => {
  if (!traits || traits.length === 0) {
    return <div className="text-gray-500">No traits found.</div>;
  }

  return (
    <div className="game-traits-viewer">
      <h2 className="text-xl font-semibold mb-2">Game Traits Viewer</h2>
      <table className="min-w-full border text-sm">
        <thead>
          <tr className="bg-gray-100">
            <th className="p-2 text-left">Trait</th>
            <th className="p-2 text-left">Description</th>
            <th className="p-2 text-left">Rarity</th>
            <th className="p-2 text-left">Game Compatibility</th>
          </tr>
        </thead>
        <tbody>
          {traits.map((trait, index) => (
            <tr key={index} className="border-t">
              <td className="p-2">{trait.name}</td>
              <td className="p-2">{trait.description}</td>
              <td className="p-2">{trait.rarity || '—'}</td>
              <td className="p-2">
                <div className="flex gap-2 flex-wrap">
                  {trait.game_effects?.minecraft && (
                    <span className="px-2 py-1 rounded bg-green-100 text-green-700">Minecraft</span>
                  )}
                  {trait.game_effects?.sims && (
                    <span className="px-2 py-1 rounded bg-pink-100 text-pink-700">Sims</span>
                  )}
                  {trait.game_effects?.unity_webgl && (
                    <span className="px-2 py-1 rounded bg-indigo-100 text-indigo-700">Unity WebGL</span>
                  )}
                  {trait.game_effects?.vrchat && (
                    <span className="px-2 py-1 rounded bg-purple-100 text-purple-700">VRChat</span>
                  )}
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default GameTraitsViewer;


