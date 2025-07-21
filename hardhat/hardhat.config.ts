import fs from "fs";
import { ethers } from "ethers";
import fetch from "node-fetch";

const CONTRACT_JSON = JSON.parse(fs.readFileSync("artifacts/contracts/XOSealsDrop.sol/XOSealsDrop.json", "utf8"));
const ABI = CONTRACT_JSON.abi;
const BYTECODE = CONTRACT_JSON.bytecode;

async function main() {
  const provider = new ethers.providers.JsonRpcProvider(process.env.NEXT_PUBLIC_RPC_BASE);
  const wallet = new ethers.Wallet(process.env.PRIVATE_KEY!, provider);

  const factory = new ethers.ContractFactory(ABI, BYTECODE, wallet);

  const BASE_URI = process.env.BASE_URI || "ipfs://QmPlaceholder/{id}.json";

  console.log("📦 Deploying with BASE_URI:", BASE_URI);
  console.log("🔑 Using wallet address:", wallet.address);
  console.log("🧪 ABI constructor args expected:", ABI.find((f: any) => f.type === "constructor"));

  const constructorFragment = ABI.find((f: any) => f.type === "constructor");

  if (constructorFragment && (constructorFragment.inputs.length > 0)) {
    throw new Error("❌ Unexpected constructor arguments found. Expected no constructor arguments.");
  }

  // Deploy contract without constructor arguments as per reverted .sol contract
  const contract = await factory.deploy();
  console.log("⏳ Awaiting deployment...");
  await contract.deployed();

  console.log(`Contract deployed at address: ${contract.address}`);

  console.log("✅ Deployment bundle pushed to GitHub.");

  const DISCORD_WEBHOOK = process.env.DISCORD_WEBHOOK;
  if (DISCORD_WEBHOOK) {
    const payload = {
      content: `📢 **New XOSealsDrop Deployment**
🔧 Branch: \`${branch}\`
🏷️ Tag: \`${tag}\`
📦 Contract: \`${contract.target}\`
🔗 GitHub: https://github.com/your-repo/commit/${shortHash}`
    };

    try {
      const res = await fetch(DISCORD_WEBHOOK, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      console.log("📣 Discord webhook sent:", await res.text());
    } catch (err) {
      console.warn("⚠️ Failed to send Discord webhook:", err);
    }
  }

  // Added block for Pulse/Vault preview creation
  const timestamp = new Date().toISOString();
  const previewDir = "vault/previews";
  fs.mkdirSync(previewDir, { recursive: true });

  const previewPath = `${previewDir}/XOSealsDrop.${timestamp}.preview.mdx`;
  const previewContent = `---
title: "Deployment: XOSealsDrop"
timestamp: "${timestamp}"
contract: "${contract.target}"
branch: "${branch}"
commit: "${shortHash}"
---

New deployment of \`XOSealsDrop\` executed on branch \`${branch}\`.

- Contract address: \`${contract.target}\`
- Git commit: \`${shortHash}\`
- Tag: \`${tag}\`
`;

  fs.writeFileSync(previewPath, previewContent);
  console.log("📝 Created Pulse/Vault preview at", previewPath);

  // Optionally pin the ABI to IPFS/Arweave
  if (process.env.PINNING_ENABLED === "true") {
    const { exec } = require("child_process");
    const abiFile = "artifacts/contracts/XOSealsDrop.sol/XOSealsDrop.json";
    exec(`npx xo-fab vault.pin ${abiFile}`, (err: any, stdout: string, stderr: string) => {
      if (err) {
        console.warn("⚠️ Failed to pin ABI to IPFS/Arweave:", stderr);
      } else {
        console.log("📤 ABI pinning result:", stdout);
      }
    });
  }
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});