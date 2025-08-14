import { useEffect, useMemo, useState } from "react";
import { BrowserProvider, Contract, JsonRpcSigner } from "ethers";

const ADDR = {
  PIGGY: process.env.NEXT_PUBLIC_PIGGY!,
};

const ABI = [
  "function totalMinted() view returns (uint256)",
  "function maxSupply() view returns (uint256)",
  "function ownerOf(uint256) view returns (address)",
  "function tokenURI(uint256) view returns (string)",
];

export default function PiggyPage() {
  const [provider, setProvider] = useState<BrowserProvider>();
  const [signer, setSigner] = useState<JsonRpcSigner>();
  const [addr, setAddr] = useState<string>();
  const [owned, setOwned] = useState<number[]>([]);
  const [images, setImages] = useState<Record<number,string>>({});

  const piggy = useMemo(()=> provider && new Contract(ADDR.PIGGY, ABI, signer || provider), [provider, signer]);

  useEffect(() => {
    if (typeof window === "undefined" || !("ethereum" in window)) return;
    setProvider(new BrowserProvider((window as any).ethereum));
  }, []);

  async function connect() {
    if (!provider) return;
    const s = await provider.getSigner();
    setSigner(s);
    setAddr(await s.getAddress());
  }

  async function refresh() {
    if (!piggy || !addr) return;
    const tm = Number(await piggy.totalMinted());
    const mine: number[] = [];
    for (let id=1; id<=tm; id++) {
      try {
        const o = await piggy.ownerOf(id);
        if (o.toLowerCase() === addr.toLowerCase()) mine.push(id);
      } catch {}
    }
    setOwned(mine);
    const out: Record<number,string> = {};
    await Promise.all(mine.map(async (id) => {
      try {
        const uri: string = await piggy.tokenURI(id);
        if (uri.startsWith("data:")) {
          const payload = uri.split(",")[1] || "";
          const json = JSON.parse(atob(payload));
          out[id] = json.image || "";
        } else {
          const r = await fetch(uri);
          const json = await r.json();
          out[id] = json.image || "";
        }
      } catch {}
    }));
    setImages(out);
  }

  return (
    <div style={{maxWidth:960, margin:"40px auto", fontFamily:"ui-sans-serif"}}>
      <h1>🐷 Piggy Bank Shield — Your Passes</h1>
      <div style={{display:"flex", gap:8}}>
        <button onClick={connect}>Connect</button>
        <button onClick={refresh} disabled={!addr}>Refresh</button>
      </div>
      {addr && <p>Connected: <b>{addr}</b></p>}
      <div style={{display:"grid", gridTemplateColumns:"repeat(auto-fill, minmax(320px,1fr))", gap:16, marginTop:16}}>
        {owned.map(id => (
          <div key={id} style={{border:"1px solid #223", borderRadius:12, overflow:"hidden"}}>
            <div style={{padding:12}}><b>Token #{id}</b></div>
            {images[id] && (
              <img src={images[id]} alt={`Piggy #${id}`} />
            )}
          </div>
        ))}
        {owned.length === 0 && <p>No Piggies yet. (Owner/airdrop only in demo)</p>}
      </div>
      <p style={{opacity:.7, marginTop:16}}>
        Image + stats render on-chain; reload to see live vault/sAETH changes.
      </p>
    </div>
  );
}
