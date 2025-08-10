import type { Trait } from '../types/traits';

type TraitsResponse = { traits: Record<string, Trait[]> } | { traits: Trait[] };

const API_BASE = 'http://localhost:8000';

async function fetchJSON<T>(url: string): Promise<T> {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json() as Promise<T>;
}

export async function getAllTraits(): Promise<Record<string, Trait[]>> {
  try {
    const data = await fetchJSON<{ success: boolean; data?: TraitsResponse }>(`${API_BASE}/api/traits`);
    if (data?.data && 'traits' in data.data && !(data.data.traits instanceof Array)) {
      return data.data.traits as Record<string, Trait[]>;
    }
    throw new Error('Malformed API response');
  } catch (_) {
    // Fallback to static file if API is down
    const fallback = await fetchJSON<{ traits: Record<string, Trait[]> }>(`/xo-games/static/traits.index.json`);
    return fallback.traits;
  }
}

export async function getDropTraits(dropId: string): Promise<Trait[]> {
  try {
    const data = await fetchJSON<{ success: boolean; data?: TraitsResponse }>(`${API_BASE}/api/traits/${dropId}`);
    if (data?.data && 'traits' in data.data && data.data.traits instanceof Array) {
      return data.data.traits as Trait[];
    }
    throw new Error('Malformed API response');
  } catch (_) {
    const all = await getAllTraits();
    return all[dropId] || [];
  }
}
