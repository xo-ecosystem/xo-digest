# XO Aether — Contracts Layer (Base Sepolia)

This workspace ships:
- **SeasonalMemecoin** (mint-on-deploy supply)
- **ShieldAether (sAETH)**: ETH-backed vault token with redeem % peg + keeper reward
- **DemoPair / DemoRouter**: tiny constant-product AMM for FLIP–sAETH
- **PiggyNFT**: free-mint window then paid mint (can gate /ops/broadcast)

## Quickstart

```bash
cp .env.example .env
# fill PRIVATE_KEY, BASE_SEPOLIA_RPC_URL, BASESCAN_API_KEY
npm i
npm run build
npm run deploy:base-sepolia
```

If deploy prints addresses, copy them to your frontend `.env.local`.

Notes
- **SeasonalMemecoin** mints full supply in the constructor (no further mint).
- **ShieldAether.deposit()** mints 1 sAETH per 1 ETH (demo). `redeemBps` (default 21%) pays a fraction of backing-per-token on redemption (modeling your “performance peg”).
- **DemoPair** skims a 0.3% swap fee to `feeTo` (set to sAETH). Call `sAETH.convertFees()` to reward keepers (pays `keeperRewardBps` from vault).
- **PiggyNFT** lets you free-mint for the first `freeMintCap` mints, then requires `priceWei`. Use token ownership on the backend to gate ops.

Security

Demo-grade. Use audits and WETH custody for production. Don’t send significant value.

---

## (Optional) Minimal capture of deployed addresses (paste into bottom of `deploy/001_deploy_all.ts` if you want a JSON file)

```ts
// after console.log("Done.");
const out = {
  network: "baseSepolia",
  SeasonalMemecoin: await memecoin.getAddress(),
  ShieldAether: await sAETH.getAddress(),
  DemoPair: await pair.getAddress(),
  DemoRouter: await router.getAddress()
};
import * as fs from "node:fs";
fs.writeFileSync(".last-deploy.json", JSON.stringify(out, null, 2));
console.log("Saved .last-deploy.json");
```

What this gives you right now
- Mint-on-deploy memecoin ✔️
- Shield Aether (sAETH) with deposit, redeem (% of backing), keeper reward ✔️
- Tiny AMM (pair + router) to demo FLIP↔sAETH swaps, fees flowing to vault ✔️
- Piggy NFT for fun gating/boosts ✔️
- Deploy to Base Sepolia with one command ✔️
