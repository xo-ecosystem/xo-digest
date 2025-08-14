import type { NextApiRequest, NextApiResponse } from "next";
import { ethers } from "ethers";
import { buildPiggyMetadata, createProvider, fetchPiggyStats } from "@/lib/piggyMeta";

// .env.local (server-side)
// RPC_URL=https://sepolia.base.org
// VAULT_ADDR=0x...
// SAETH_ADDR=0x...
// MEME_ADDR=0x...
// PIGGY_ADDR=0x...

const RPC_URL = process.env.RPC_URL || "";
const VAULT_ADDR = process.env.VAULT_ADDR || "";
const SAETH_ADDR = process.env.SAETH_ADDR || "";
const MEME_ADDR = process.env.MEME_ADDR || "";
const PIGGY_ADDR = process.env.PIGGY_ADDR || "";

const ERC20_ABI = [
  "function totalSupply() view returns (uint256)",
  "function decimals() view returns (uint8)",
  "function backingPerToken_wei1e18() view returns (uint256)",
];

function svgToDataURI(svg: string): string {
  const encoded = encodeURIComponent(svg).replace(/'/g, "%27").replace(/"/g, "%22");
  return `data:image/svg+xml;charset=utf-8,${encoded}`;
}

function formatEth(wei: bigint) {
  return Number(ethers.formatEther(wei));
}

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  try {
    const { id } = req.query;
    const tokenId = Array.isArray(id) ? id[0] : id;
    const style = (Array.isArray(req.query.style) ? req.query.style[0] : req.query.style) as string | undefined;

    if (!tokenId || !/^\d+$/.test(tokenId)) {
      res.status(400).json({ error: "invalid token id" });
      return;
    }
    if (!RPC_URL) {
      res.status(500).json({ error: "RPC_URL not configured" });
      return;
    }

    const provider = createProvider(RPC_URL);
    const stats = await fetchPiggyStats(provider, { vaultAddr: VAULT_ADDR || undefined, saethAddr: SAETH_ADDR || undefined });
    const proto = (req.headers["x-forwarded-proto"] as string) || "http";
    const host = (req.headers.host as string) || "localhost:3000";
    const metadata = buildPiggyMetadata(tokenId, stats, { piggyAddr: PIGGY_ADDR || undefined, memeAddr: MEME_ADDR || undefined, proto, host, style });

    res.setHeader("Content-Type", "application/json");
    res.setHeader("Cache-Control", "public, max-age=30, s-maxage=60, stale-while-revalidate=120");
    res.status(200).json(metadata);
  } catch (err: any) {
    res.status(500).json({ error: err?.message || "server error" });
  }
}
