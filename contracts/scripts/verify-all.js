import { execSync } from "node:child_process";
import * as fs from "node:fs";

const net = process.argv[2] || "baseSepolia";
const addressesPath = ".last-deploy.json";

if (!fs.existsSync(addressesPath)) {
  console.log("No .last-deploy.json with constructor args — run deployment with capture if needed.");
  process.exit(0);
}

// (Optional) If you later store constructor args, loop and verify here.
// For now, just print a reminder:
console.log("Run individual verifications as needed, e.g.:");
console.log(`npx hardhat verify --network ${net} <address> <constructor args...>`);

// (Simple stub; for full auto-verify, capture addresses & args in the deploy script and write to .last-deploy.json.)
