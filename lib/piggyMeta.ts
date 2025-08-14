import { ethers } from "ethers";

export type PiggyStats = {
  vaultBackingEth?: number;
  sAethSupply?: number;
  backingPerTokenEth?: number;
  blockNumber?: number;
};

export function createProvider(rpcUrl: string) {
  return new ethers.JsonRpcProvider(rpcUrl);
}

function formatEth(wei: bigint) {
  return Number(ethers.formatEther(wei));
}

const ERC20_ABI = [
  "function totalSupply() view returns (uint256)",
  "function decimals() view returns (uint8)",
  "function backingPerToken_wei1e18() view returns (uint256)",
];

export async function fetchPiggyStats(provider: ethers.JsonRpcProvider, opts: { vaultAddr?: string; saethAddr?: string; }) {
  const stats: PiggyStats = {};
  try {
    stats.blockNumber = await provider.getBlockNumber();
  } catch {}

  if (opts.vaultAddr) {
    try {
      const backingWei: bigint = await provider.getBalance(opts.vaultAddr);
      stats.vaultBackingEth = formatEth(backingWei);
    } catch {}
  }

  if (opts.saethAddr) {
    try {
      const sa = new ethers.Contract(opts.saethAddr, ERC20_ABI, provider);
      const [supplyRaw, dec] = await Promise.all([sa.totalSupply(), sa.decimals()]);
      const scale = 10n ** BigInt(dec);
      stats.sAethSupply = Number(supplyRaw) / Number(scale);
      try {
        const bpt = (await sa.backingPerToken_wei1e18()) as bigint;
        stats.backingPerTokenEth = formatEth(bpt);
      } catch {}
    } catch {}
  }

  return stats;
}

export function buildPiggySvg(tokenId: string, stats: PiggyStats, style?: string) {
  const preset = (style || "minimal").toLowerCase();
  const gradientA = preset === "dark" ? "#0B1020" : preset === "meme" ? "#8AF1FF" : "#FF85A1";
  const gradientB = preset === "dark" ? "#1A2444" : preset === "meme" ? "#FFD18A" : "#FFE08A";
  const cardFill = preset === "dark" ? "#0f1429" : "white";
  const titleFill = preset === "dark" ? "#F5F7FF" : "#111";
  const subFill = preset === "dark" ? "#A8B3D9" : "#555";
  const statFill = titleFill;

  const title = `Piggy #${tokenId}`;
  const subtitle = `Shield Aether Piggy Pass`;
  const line1 = stats.vaultBackingEth != null
    ? `Vault Backing: ${stats.vaultBackingEth.toFixed(4)} ETH`
    : `Vault Backing: (n/a)`;
  const line2 = stats.sAethSupply != null
    ? `sAETH Supply: ${stats.sAethSupply.toLocaleString()}`
    : `sAETH Supply: (n/a)`;
  const line3 = stats.backingPerTokenEth != null
    ? `Backing/1 sAETH: ${stats.backingPerTokenEth.toFixed(6)} ETH`
    : ``;
  const now = new Date().toISOString();
  const sig = stats.blockNumber != null ? `block #${stats.blockNumber}` : "";

  return `<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="800" height="420">
  <defs>
    <linearGradient id="g" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="${gradientA}"/>
      <stop offset="100%" stop-color="${gradientB}"/>
    </linearGradient>
    <filter id="shadow" x="-30%" y="-30%" width="160%" height="160%">
      <feDropShadow dx="0" dy="4" stdDeviation="8" flood-color="rgba(0,0,0,0.25)"/>
    </filter>
  </defs>
  <rect x="0" y="0" width="800" height="420" fill="url(#g)"/>
  <g transform="translate(32,32)">
    <rect width="736" height="356" rx="24" fill="${cardFill}" filter="url(#shadow)"/>
    <g transform="translate(24,24)">
      <text x="0" y="28" font-family="Inter, system-ui, -apple-system" font-weight="700" font-size="24" fill="${titleFill}">${title}</text>
      <text x="0" y="56" font-family="Inter, system-ui, -apple-system" font-weight="500" font-size="16" fill="${subFill}">${subtitle}</text>

      <g transform="translate(0,84)">
        <circle cx="64" cy="64" r="64" fill="#FFC4D0"/>
        <rect x="40" y="28" width="48" height="8" rx="3" fill="#A64E5F"/>
        <ellipse cx="64" cy="84" rx="22" ry="16" fill="#FF9FB3" stroke="#A64E5F" stroke-width="3"/>
        <circle cx="52" cy="80" r="5" fill="#A64E5F"/>
        <circle cx="76" cy="80" r="5" fill="#A64E5F"/>
      </g>

      <g transform="translate(160,88)">
        <text x="0" y="0" font-family="Inter, system-ui, -apple-system" font-size="14" fill="${subFill}">Stats</text>
        <text x="0" y="28" font-family="Inter, system-ui, -apple-system" font-size="18" fill="${statFill}">${line1}</text>
        <text x="0" y="56" font-family="Inter, system-ui, -apple-system" font-size="18" fill="${statFill}">${line2}</text>
        ${line3 ? `<text x="0" y="84" font-family="Inter, system-ui, -apple-system" font-size="18" fill="${statFill}">${line3}</text>` : ``}
      </g>

      <text x="0" y="330" font-family="Inter, system-ui, -apple-system" font-size="12" fill="${subFill}">${now} ${sig}</text>
    </g>
  </g>
</svg>`;
}

function svgToDataURI(svg: string): string {
  const encoded = encodeURIComponent(svg).replace(/'/g, "%27").replace(/"/g, "%22");
  return `data:image/svg+xml;charset=utf-8,${encoded}`;
}

export function buildPiggyMetadata(
  tokenId: string,
  stats: PiggyStats,
  opts: { piggyAddr?: string; memeAddr?: string; proto: string; host: string; style?: string }
) {
  const svg = buildPiggySvg(tokenId, stats, opts.style);
  const imageData = svgToDataURI(svg);
  const imageUrl = `${opts.proto}://${opts.host}/api/piggy/image/${tokenId}${opts.style ? `?style=${encodeURIComponent(opts.style)}` : ""}`;

  const attributes: Array<{ trait_type: string; value: string | number }> = [];
  if (stats.vaultBackingEth != null) attributes.push({ trait_type: "Vault Backing (ETH)", value: Number(stats.vaultBackingEth.toFixed(6)) });
  if (stats.sAethSupply != null) attributes.push({ trait_type: "sAETH Supply", value: stats.sAethSupply });
  if (stats.backingPerTokenEth != null) attributes.push({ trait_type: "Backing/1 sAETH (ETH)", value: Number(stats.backingPerTokenEth.toFixed(8)) });
  if (opts.memeAddr) attributes.push({ trait_type: "Memecoin Paired", value: opts.memeAddr });

  return {
    name: `Piggy #${tokenId}`,
    description: "Piggy Pass for Shield Aether — dynamic metadata reflecting vault backing and sAETH supply.",
    external_url: opts.piggyAddr ? `https://sepolia.basescan.org/address/${opts.piggyAddr}` : undefined,
    image: imageUrl,
    image_data: imageData,
    attributes,
  };
}
