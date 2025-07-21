import { ethers } from "hardhat";
import fs from "fs";
import path from "path";
import { execSync } from "child_process";

async function main() {
  import dotenv from "dotenv";
  dotenv.config();
  const network = await ethers.provider.getNetwork();
  const isMainnet = network.name === "homestead";
  const baseUri = process.env.XO_DROP_URI || "ipfs://placeholder/{id}.json";

  const XOSealsDrop = await ethers.getContractFactory("XOSealsDrop");
  const ownerAddress = await ethers.resolveName(process.env.XO_INITIAL_OWNER || (await ethers.getSigners())[0].address);
  const xoDrop = await XOSealsDrop.deploy(baseUri, ownerAddress);
  await xoDrop.deployed();

  if (!isMainnet) {
    const [owner] = await ethers.getSigners();
    const tx = await xoDrop.mint(owner.address, 1, 1, "0x");
    await tx.wait();
    console.log("🧪 Simulated mint to:", owner.address);
  }

  const address = xoDrop.address;
  console.log("🚀 XOSealsDrop deployed to:", address);

  const outDir = path.resolve(__dirname, "../preview");
  if (!fs.existsSync(outDir)) fs.mkdirSync(outDir);

  const gitBranch = execSync("git rev-parse --abbrev-ref HEAD").toString().trim();
  const gitCommit = execSync("git rev-parse HEAD").toString().trim();
  const timestamp = new Date().toISOString();

  const previewContent = `---
title: "XOSealsDrop Deployment"
contract: "XOSealsDrop"
address: "${address}"
branch: "${gitBranch}"
commit: "${gitCommit}"
date: "${timestamp}"
---

Deployment completed for \`XOSealsDrop\` at \`${address}\`.

🔖 Git: \`${gitBranch}@${gitCommit.slice(0, 7)}\`
📅 Date: ${timestamp}
`;

  fs.writeFileSync(path.join(outDir, "XOSealsDrop.preview.mdx"), previewContent);

  const previewLog = {
    address,
    baseUri,
    gitBranch,
    gitCommit,
    timestamp,
    network: network.name,
  };
  fs.writeFileSync(path.join(outDir, "XOSealsDrop.preview.log"), JSON.stringify(previewLog, null, 2));

  const abiPath = path.resolve(__dirname, `../artifacts/contracts/XOSealsDrop.sol/XOSealsDrop.json`);
  if (fs.existsSync(abiPath)) {
    try {
      execSync(`xo-fab vault.pin ${abiPath}`);
      console.log("📦 ABI pinned successfully.");
    } catch (e) {
      console.warn("⚠️ ABI pinning failed:", e.message);
    }
  }

  execSync("git add .");
  execSync(`git commit -m '🚀 Deployed XOSealsDrop to ${address}'`);
  execSync("git push");

  const webhookURL = process.env.XO_DISCORD_WEBHOOK;
  if (webhookURL) {
    const payload = {
      content: `📡 **XOSealsDrop Deployed!**
> Network: \`ethereum\`
> Contract: \`${address}\`
> Git: \`${gitBranch}@${gitCommit.slice(0, 7)}\`
🔗 Explorer: https://etherscan.io/address/${address}`
    };

    await fetch(webhookURL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
  }
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});