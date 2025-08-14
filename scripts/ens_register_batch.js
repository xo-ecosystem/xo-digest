// scripts/ens_register_batch.js
// Usage:
//   env RPC_URL="https://mainnet.infura.io/v3/..." PK=0x<privkey> node scripts/ens_register_batch.js \
//     --owner 0xYourAddr --years 1 --set-addr 0xYourAddr \
//     --text xo.signer=0xYourAddr --text xo.receipts=ipfs://<cid> \
//     [--commit-only | --reveal | --simulate | --rent-only]  xoseal.eth xosealed.eth xodigest.eth
//
// What it does (default end-to-end):
//  1) For each name: commit -> waits minCommitmentAge -> register for N years
//  2) Sets Public Resolver and (optionally) ADDR + TEXT records
//
// New flags:
//  --commit-only : only submit commitments, stash secret in ~/.config/xo-ens/commit-<label>.json
//  --reveal      : only perform register using stashed secret (must be >= minCommitmentAge old)
//  --simulate    : print rent price + gas estimate (no tx sent)
//  --rent-only  : alias for --simulate; prints rent price + gas estimate (no tx sent)

import { ethers, namehash, getAddress } from "ethers";
import fs from "fs";
import os from "os";
import path from "path";
import contentHash from "content-hash";
import punycode from "punycode/punycode.js";
import 'dotenv/config';
// ---- ENS mainnet addresses (EP3.5, Jul 2025): https://docs.ens.domains/learn/deployments
const ENS_REGISTRY = "0x00000000000C2E074eC69A0dFb2997BA6C7d2e1e"; // unchanged
const ETH_REGISTRAR_CTRL = "0x253553366Da8546fC250F225fe3d25d0C782303b"; // new controller
const PUBLIC_RESOLVER = "0x231b0Ee14048e9dCcD1d247744d114a4EB5E8E63"; // new public resolver

// Minimal ABIs
const CTRL_ABI = [
  "function minCommitmentAge() view returns (uint256)",
  "function rentPrice(string name, uint256 duration) view returns (uint256)",
  "function available(string name) view returns (bool)",
  "function makeCommitment(string name,address owner,uint256 duration,bytes32 secret,address resolver,bytes[] data,bool reverseRecord,uint16 ownerControlledFuses) view returns (bytes32)",
  "function commit(bytes32 commitment)",
  "function register(string name,address owner,uint256 duration,bytes32 secret,address resolver,bytes[] data,bool reverseRecord,uint16 ownerControlledFuses) payable",
];
const REG_ABI = [
  "function owner(bytes32 node) view returns (address)",
  "function setResolver(bytes32 node,address resolver)",
];
const RES_ABI = [
  "function setAddr(bytes32 node,uint256 coinType,bytes calldata a)",
  "function setText(bytes32 node,string key,string value)",
  "function setContenthash(bytes32 node, bytes hash)"
];

function parseArgs() {
  const args = process.argv.slice(2);
  const names = [];
  const opts = { owner: null, years: 1, addr: null, texts: [], commitOnly: false, reveal: false, simulate: false, contenthash: null };
  for (let i = 0; i < args.length; i++) {
    const a = args[i];
    if (a === "--owner") opts.owner = getAddress(args[++i]);
    else if (a === "--years") opts.years = Number(args[++i] || "1");
    else if (a === "--set-addr") opts.addr = getAddress(args[++i]);
    else if (a === "--text") {
      const kv = (args[++i] || "").split("=");
      if (kv.length >= 2) opts.texts.push([kv[0], kv.slice(1).join("=")]);
    } else if (a === "--contenthash") { opts.contenthash = (args[++i] || ""); }
    else if (a === "--commit-only") { opts.commitOnly = true; }
    else if (a === "--reveal") { opts.reveal = true; }
    else if (a === "--simulate") { opts.simulate = true; }
    else if (a === "--rent-only") { opts.simulate = true; }
    else if (a.startsWith("--")) {
      console.error("Unknown flag:", a); process.exit(1);
    } else {
      names.push(a);
    }
  }
  if (!opts.owner) { console.error("Missing --owner"); process.exit(1); }
  if (names.length === 0) { console.error("Provide at least one .eth name"); process.exit(1); }
  if (opts.commitOnly && opts.reveal) { console.error("Use either --commit-only or --reveal, not both."); process.exit(1); }
  return { names, opts };
}

function labelFromName(name) {
  const parts = name.split(".");
  if (parts.length !== 2 || parts[1].toLowerCase() !== "eth") {
    throw new Error(`Only second-level .eth supported: ${name}`);
  }
  // Normalize any Unicode/emoji to punycode per UTS-46
  const labelAscii = punycode.toASCII(parts[0], { useStd3ASCII: true, transitional: false });
  if (!labelAscii) throw new Error(`Invalid ENS label: ${parts[0]}`);
  return labelAscii.toLowerCase();
}

const commitDir = path.join(os.homedir(), ".config", "xo-ens");
function ensureCommitDir() { fs.mkdirSync(commitDir, { recursive: true }); }
function commitFile(label) { return path.join(commitDir, `commit-${label}.json`); }

function saveCommit(label, data) {
  ensureCommitDir();
  fs.writeFileSync(commitFile(label), JSON.stringify(data, null, 2));
}
function loadCommit(label) {
  try { return JSON.parse(fs.readFileSync(commitFile(label), "utf8")); }
  catch { return null; }
}

function encodeContenthash(uri) {
  if (!uri) return null;
  const lower = uri.toLowerCase();
  if (lower.startsWith("ipfs://")) {
    const cid = uri.slice(7);
    return "0x" + contentHash.encode("ipfs-ns", cid);
  } else if (lower.startsWith("ipns://")) {
    const name = uri.slice(7);
    return "0x" + contentHash.encode("ipns-ns", name);
  }
  throw new Error(`Unsupported --contenthash scheme (use ipfs:// or ipns://): ${uri}`);
}

async function main() {
  const { names, opts } = parseArgs();
  const rpc = process.env.RPC_URL;
  if (!rpc) { console.error("Missing RPC_URL"); process.exit(1); }
  const provider = new ethers.JsonRpcProvider(rpc);

  // Only require a PK when we are going to send transactions
  let wallet = null;
  let signerOrProvider = provider;
  const needsSigning = !(opts.simulate); // commit/reveal/register paths need signing

  if (needsSigning) {
    const pk = process.env.PK;
    if (!pk) { console.error("Missing PK (0x...)"); process.exit(1); }
    wallet = new ethers.Wallet(pk, provider);
    signerOrProvider = wallet;
  }

  const ctrl = new ethers.Contract(ETH_REGISTRAR_CTRL, CTRL_ABI, signerOrProvider);
  const reg = new ethers.Contract(ENS_REGISTRY, REG_ABI, signerOrProvider);
  const res = new ethers.Contract(PUBLIC_RESOLVER, RES_ABI, signerOrProvider);

  const minAge = Number(await ctrl.minCommitmentAge());
  const duration = Math.max(31536000 * opts.years, 31536000); // seconds

  const encodedCH = opts.contenthash ? encodeContenthash(opts.contenthash) : null;

  console.log(`Using owner=${opts.owner}, years=${opts.years}, minCommitmentAge=${minAge}s`);
  for (const fullName of names) {
    const label = labelFromName(fullName);
    const fullAscii = `${label}.eth`;
    const node = namehash(fullAscii);

    // Check label availability via controller (fast path); if owned, skip early
    try {
      const isAvail = await ctrl.available(label);
      if (!isAvail && !opts.reveal) {
        console.error(`❌ ${fullName} is not available (controller.available=false). Skipping.`);
        continue;
      }
    } catch (_) {
      // Some controller versions may not expose available(); ignore on error
    }

    if (!opts.reveal) {
      const currentOwner = await reg.owner(node);
      if (currentOwner !== ethers.ZeroAddress && currentOwner.toLowerCase() !== opts.owner.toLowerCase()) {
        console.error(`❌ ${fullName} is already owned by ${currentOwner}. Skipping.`);
        continue;
      }
    }

    let secret, commitment;
    if (opts.reveal) {
      const stash = loadCommit(label);
      if (!stash) { console.error(`❌ No stash for ${label}. Run --commit-only first.`); continue; }
      secret = stash.secret;
      commitment = stash.commitment;
      const ageSec = Math.floor((Date.now() - stash.timestampMs) / 1000);
      if (ageSec < minAge) {
        console.error(`⏳ ${fullAscii}: commitment is only ${ageSec}s old; need >= ${minAge}s. Try later.`);
        continue;
      }
    } else {
      secret = ethers.hexlify(ethers.randomBytes(32));
      commitment = await ctrl.makeCommitment(label, opts.owner, duration, secret, ethers.ZeroAddress, [], false, 0);
    }

    const price = await ctrl.rentPrice(label, duration);
    if (opts.simulate) {
      // Always show rent price; try to estimate gas but it can revert if there is no valid commitment aged >= minCommitmentAge
      let gasStr = "n/a";
      let gasNote = "";
      try {
        const tx = await ctrl.register.populateTransaction(
          label, opts.owner, duration, secret, ethers.ZeroAddress, [], false, 0,
          { value: price }
        );
        const gas = await provider.estimateGas({ ...tx, from: opts.owner, value: price });
        gasStr = gas.toString();
      } catch (e) {
        gasNote = " (no aged commitment yet; register gas estimate not available)";
      }
      console.log(`[SIMULATE] ${fullAscii}: rentPrice=${ethers.formatEther(price)} ETH, estGas=${gasStr}${gasNote}${encodedCH ? ", will set contenthash" : ""}`);
      continue;
    }

    if (opts.reveal) {
      console.log(`→ ${fullAscii}: reveal (register)`);
    } else {
      console.log(`→ ${fullAscii}: commit ${commitment}`);
      await (await ctrl.commit(commitment)).wait();
      saveCommit(label, { name: fullName, label, commitment, secret, duration, owner: opts.owner, timestampMs: Date.now() });
      console.log(`   stashed secret at ${commitFile(label)}`);
      if (opts.commitOnly) {
        const eta = new Date(Date.now() + (minAge * 1000));
        console.log(`✓ committed. Earliest reveal after: ${eta.toISOString()}`);
        continue;
      }
      console.log(`   waiting ${minAge}s (minCommitmentAge) before reveal...`);
      await new Promise(r => setTimeout(r, (minAge + 1) * 1000));
    }

    console.log(`   rentPrice=${ethers.formatEther(price)} ETH for ${opts.years}y`);
    const tx = await ctrl.register(label, opts.owner, duration, secret, ethers.ZeroAddress, [], false, 0, { value: price });
    const rcpt = await tx.wait();
    console.log(`✅ registered ${fullAscii} in tx ${rcpt.hash}`);

    await (await reg.setResolver(node, PUBLIC_RESOLVER)).wait();
    console.log(`   resolver -> ${PUBLIC_RESOLVER}`);

    if (opts.addr) {
      const coinTypeEth = 60n;
      const addrBytes = ethers.getBytes(opts.addr);
      await (await res.setAddr(node, coinTypeEth, addrBytes)).wait();
      console.log(`   setAddr[ETH]=${opts.addr}`);
    }
    for (const [k, v] of opts.texts) {
      await (await res.setText(node, k, v)).wait();
      console.log(`   setText ${k}=${v}`);
    }
    if (encodedCH) {
      await (await res.setContenthash(node, encodedCH)).wait();
      console.log(`   setContenthash=${opts.contenthash}`);
    }

    console.log(`🎉 done: ${fullAscii}`);
  }
}

main().catch(e => { console.error(e); process.exit(1); });
