// src/hooks/useHandleRegistry.ts
import { useEffect, useState } from "react";

export interface HandlePlatformStatus {
  handle: string;
  available: boolean | null;
}

export interface HandleRegistryEntry {
  domain: string;
  handle: string;
  platforms: Record<string, HandlePlatformStatus>;
}

export function useHandleRegistry(path = "/vault/registry/handles.json") {
  const [data, setData] = useState<HandleRegistryEntry[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(path)
      .then((res) => res.json())
      .then(setData)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [path]);

  return { data, loading };
}
