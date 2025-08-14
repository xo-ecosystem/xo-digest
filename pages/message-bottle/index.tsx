import Head from "next/head";
import { useEffect, useState } from "react";

type Cfg = {
  collections: {
    community: { name:string; symbol:string; price_eth:string; max_supply:number };
    brie: { name:string; symbol:string; price_eth:string; max_supply:number };
  };
};

export default function MessageBottlePage() {
  const [cfg, setCfg] = useState<Cfg | null>(null);
  const [addr, setAddr] = useState("");
  const [minting, setMinting] = useState<null | "community" | "brie">(null);
  const [lastTx, setLastTx] = useState<string | null>(null);

  useEffect(() => {
    (async () => {
      const res = await fetch("/config/message_bottle.json");
      setCfg(await res.json());
    })();
  }, []);

  const mint = async (edition: "community" | "brie") => {
    if (!addr) { alert("Enter destination wallet address first"); return; }
    setMinting(edition);
    setLastTx(null);
    try {
      const r = await fetch("/api/mint/message-bottle", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ edition, to: addr })
      }).then(r => r.json());
      if (!r.ok) throw new Error(r.error || "mint failed");
      setLastTx(r.txHash);
    } catch (e:any) {
      alert(e.message || "mint failed");
    } finally {
      setMinting(null);
    }
  };

  if (!cfg) return <div className="p-8">Loading…</div>;

  const c = cfg.collections.community;
  const b = cfg.collections.brie;

  return (
    <>
      <Head><title>XO Message Bottle</title></Head>
      <main className="min-h-screen p-6 flex flex-col gap-6">
        <h1 className="text-3xl font-semibold">XO Message Bottle</h1>
        <p className="opacity-75">A little wave from the XO Sea 🌊 — two editions at launch.</p>

        <div className="max-w-xl">
          <label className="block text-sm mb-1">Destination wallet (EVM)</label>
          <input
            value={addr}
            onChange={(e)=>setAddr(e.target.value)}
            placeholder="0x…"
            className="w-full border rounded px-3 py-2"
          />
          <p className="text-xs opacity-60 mt-1">No wallet connect yet — manual entry for MVP.</p>
        </div>

        <section className="grid md:grid-cols-2 gap-6">
          <article className="border rounded-2xl p-5">
            <h2 className="text-xl font-semibold">{c.name}</h2>
            <p className="opacity-70">Supply: {c.max_supply} • Price: {c.price_eth} ETH</p>
            <img src="/logo_goldfish.png" alt="XO" className="w-24 mt-3" />
            <div className="mt-4 flex gap-3">
              <a href="/metadata/message-bottle/community.json" className="text-sm underline">Metadata JSON</a>
              <button
                onClick={()=>mint("community")}
                disabled={!!minting}
                className="px-4 py-2 rounded bg-black text-white disabled:opacity-50"
              >
                {minting==="community" ? "Minting…" : "Mint"}
              </button>
            </div>
          </article>

          <article className="border rounded-2xl p-5">
            <h2 className="text-xl font-semibold">{b.name}</h2>
            <p className="opacity-70">Supply: {b.max_supply} • Price: {b.price_eth} ETH</p>
            <img src="/logo_goldfish.png" alt="XO" className="w-24 mt-3" />
            <div className="mt-4 flex gap-3">
              <a href="/metadata/message-bottle/brie.json" className="text-sm underline">Metadata JSON</a>
              <button
                onClick={()=>mint("brie")}
                disabled={!!minting}
                className="px-4 py-2 rounded bg-black text-white disabled:opacity-50"
              >
                {minting==="brie" ? "Minting…" : "Mint 1/1"}
              </button>
            </div>
          </article>
        </section>

        {lastTx && (
          <div className="mt-4 p-3 bg-green-50 border rounded">
            <div className="text-sm">Submitted tx:</div>
            <code className="break-all text-xs">{lastTx}</code>
          </div>
        )}
      </main>
    </>
  );
}
