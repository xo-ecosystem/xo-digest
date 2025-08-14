import type { NextApiRequest, NextApiResponse } from "next";
import { buildPiggySvg, createProvider, fetchPiggyStats } from "../../../lib/piggyMeta";

const RPC_URL = process.env.RPC_URL || "";
const VAULT_ADDR = process.env.VAULT_ADDR || ""; // optional
const SAETH_ADDR = process.env.SAETH_ADDR || ""; // optional

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  try {
    const tokenId = Array.isArray(req.query.id) ? req.query.id[0] : req.query.id;
    const style = (Array.isArray(req.query.style) ? req.query.style[0] : req.query.style) as string | undefined;
    if (!tokenId || !/^\d+$/.test(tokenId)) {
      res.status(400).send("invalid token id");
      return;
    }
    if (!RPC_URL) {
      res.status(500).send("RPC_URL not configured");
      return;
    }

    const provider = createProvider(RPC_URL);
    const stats = await fetchPiggyStats(provider, { vaultAddr: VAULT_ADDR || undefined, saethAddr: SAETH_ADDR || undefined });
    const svg = buildPiggySvg(tokenId as string, stats, style);

    res.setHeader("Content-Type", "image/svg+xml; charset=utf-8");
    res.setHeader("Cache-Control", "public, max-age=30, s-maxage=60, stale-while-revalidate=120");
    res.status(200).send(svg);
  } catch (e: any) {
    res.status(500).send(e?.message || "server error");
  }
}
