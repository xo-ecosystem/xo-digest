import type { NextApiRequest, NextApiResponse } from "next";

/**
 * Stub endpoint for mint requests.
 * Later: verify wallet, build payload, call relayer/signer, return tx hash.
 */
export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== "POST") return res.status(405).json({ error: "Method not allowed" });

  try {
    const { edition, to } = req.body || {};
    if (!edition || !to) return res.status(400).json({ error: "Missing 'edition' or 'to'." });

    // TODO: put your contract interaction here.
    // For now we simulate a success and echo a fake hash.
    const fakeTxHash = "0x" + "bottle".padEnd(64, "0");

    return res.status(200).json({
      ok: true,
      edition,
      to,
      txHash: fakeTxHash
    });
  } catch (err: any) {
    return res.status(500).json({ error: err?.message || "mint failed" });
  }
}

import type { NextApiRequest, NextApiResponse } from "next";

/**
 * Stub endpoint for mint requests.
 * Later: verify wallet, build payload, call relayer/signer, return tx hash.
 */
export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== "POST") return res.status(405).json({ error: "Method not allowed" });

  try {
    const { edition, to } = req.body || {};
    if (!edition || !to) return res.status(400).json({ error: "Missing 'edition' or 'to'." });

    // TODO: put your contract interaction here.
    // For now we simulate a success and echo a fake hash.
    const fakeTxHash = "0x" + "bottle".padEnd(64, "0");

    return res.status(200).json({
      ok: true,
      edition,
      to,
      txHash: fakeTxHash
    });
  } catch (err: any) {
    return res.status(500).json({ error: err?.message || "mint failed" });
  }
}
