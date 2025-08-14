#!/usr/bin/env node
// Minimal hot->cold sweep using ethers v6
import { ethers } from "ethers";

const rpc = process.env.XO_ETH_RPC_URL;
const chainId = Number(process.env.XO_ETH_CHAIN_ID || "1");
const cold = process.env.XO_ETH_COLD_ADDRESS;
const threshEth = Number(process.env.XO_ETH_SWEEP_THRESHOLD_ETH || "0.25");

// Prefer Keychain fetch via shell if no env key
async function getPrivKey() {
  if (process.env.XO_WALLET_PRIVATE_KEY) return process.env.XO_WALLET_PRIVATE_KEY;
  const { execSync } = await import("child_process");
  try {
    const out = execSync(`${process.cwd()}/scripts/wallet_store_keychain.sh get xo-hot`, {encoding:"utf8"});
    return out.trim();
  } catch {
    throw new Error("No private key available (set XO_WALLET_PRIVATE_KEY or store in Keychain)");
  }
}

async function main() {
  if (!rpc || !cold) throw new Error("Missing XO_ETH_RPC_URL or XO_ETH_COLD_ADDRESS envs");
  const pk = await getPrivKey();
  const provider = new ethers.JsonRpcProvider(rpc, { chainId });
  const wallet = new ethers.Wallet(pk, provider);

  const bal = await provider.getBalance(wallet.address);
  const balEth = Number(ethers.formatEther(bal));
  if (balEth <= threshEth) {
    console.log(`Balance ${balEth} ETH <= threshold ${threshEth}, nothing to sweep.`);
    return;
  }
  const fee = await provider.getFeeData();
  const gasLimit = 21000n;
  const maxFeePerGas = fee.maxFeePerGas ?? fee.gasPrice ?? ethers.parseUnits("20", "gwei");
  const maxPriorityFeePerGas = fee.maxPriorityFeePerGas ?? ethers.parseUnits("1.5", "gwei");
  const cost = gasLimit * maxFeePerGas;
  const value = bal - cost; // sweep rest

  if (value <= 0n) throw new Error("Not enough to cover gas");

  const tx = await wallet.sendTransaction({
    to: cold,
    value,
    maxFeePerGas,
    maxPriorityFeePerGas,
    gasLimit,
  });
  console.log("🚀 sweep tx:", tx.hash);
  const rcpt = await tx.wait();
  console.log("✅ confirmed in block", rcpt.blockNumber);
}
main().catch(e => { console.error("❌", e.message || e); process.exit(1); });
