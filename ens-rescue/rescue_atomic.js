// ENS Rescue — Flashbots private bundle (ethers v5)
// - Funds compromised wallet just-in-time
// - Transfers ENS .eth NFT (BaseRegistrar) to NEW_OWNER atomically
// - Retries across a few blocks with aggressive, configurable tips

const path = require("path");
const dotenv = require("dotenv");

// load root .env if present, then local .env
dotenv.config({ path: path.resolve(__dirname, "..", ".env") });
dotenv.config();

const ethers = require("ethers");
const { FlashbotsBundleProvider } = require("@flashbots/ethers-provider-bundle");

// ---- Constants (v5) ----
const CHAIN = "mainnet";
const ENS_BASE_REGISTRAR = "0x57f1887a8BF19b14fC0dF6fD9B2aAcC9Af147eA85"; // .eth ERC-721
const ERC721_ABI = [
  "function ownerOf(uint256 tokenId) view returns (address)",
  "function safeTransferFrom(address from, address to, uint256 tokenId) external",
];

// ======= CONFIG =======
const NAME = process.env.LABEL || "xoseals"; // label before .eth
const TOKEN_ID = ethers.BigNumber.from(
  ethers.utils.keccak256(ethers.utils.toUtf8Bytes(NAME))
);

// fees & retries
const MAX_PRIORITY_GWEI = process.env.MAX_PRIORITY_GWEI
  ? ethers.utils.parseUnits(process.env.MAX_PRIORITY_GWEI, "gwei")
  : ethers.utils.parseUnits("20", "gwei"); // default 20 gwei

const FEE_MULTIPLIER = Number(process.env.FEE_MULTIPLIER || "2"); // baseFee * 2 + tip
const RETRY_BLOCKS = Number(process.env.RETRY_BLOCKS || "8");      // extra blocks to try

const FUND_BUFFER_ETH = process.env.FUND_BUFFER_ETH
  ? ethers.utils.parseEther(process.env.FUND_BUFFER_ETH)
  : ethers.utils.parseEther("0.003"); // default 0.003 ETH buffer

// ======= MAIN =======
async function main() {
  assertV5();

  // Providers & signers
  const provider = new ethers.providers.JsonRpcProvider(env("RPC_URL"));
  const funder = new ethers.Wallet(env("FUNDER_KEY"), provider);
  const compromised = new ethers.Wallet(env("COMPROMISED_KEY"), provider);
  const newOwner = ethers.utils.getAddress(env("NEW_OWNER"));

  const registrar = new ethers.Contract(ENS_BASE_REGISTRAR, ERC721_ABI, provider);

  // Preflight
  const net = await provider.getNetwork();
  if (net.chainId !== 1) throw new Error(`Not on mainnet (chainId=${net.chainId})`);

  const onChainOwner = await registrar.ownerOf(TOKEN_ID);
  if (ethers.utils.getAddress(onChainOwner) !== compromised.address) {
    throw new Error(
      `Token not owned by compromised address.\n current owner: ${onChainOwner}\n compromised: ${compromised.address}`
    );
  }

  // Flashbots (auth signer can be any wallet; reuse funder)
  const flashbots = await FlashbotsBundleProvider.create(
    provider,
    funder,
    "https://relay.flashbots.net",
    CHAIN
  );

  // Build transfer tx (populate first to get data)
  const txTransfer = await registrar
    .connect(compromised)
    .populateTransaction.safeTransferFrom(compromised.address, newOwner, TOKEN_ID);

  // Gas parameters
  const block = await provider.getBlock("latest");
  const baseFee = block.baseFeePerGas || ethers.BigNumber.from("0");
  const maxPriorityFeePerGas = MAX_PRIORITY_GWEI;
  const maxFeePerGas = baseFee.mul(FEE_MULTIPLIER).add(maxPriorityFeePerGas);

  const gasEstimateTransfer = await provider.estimateGas({
    from: compromised.address,
    to: ENS_BASE_REGISTRAR,
    data: txTransfer.data,
  });

  // exact gas funds + buffer
  const requiredWei = gasEstimateTransfer.mul(maxFeePerGas).add(FUND_BUFFER_ETH);

  // Funding tx (simple ETH send)
  const txFund = {
    to: compromised.address,
    value: requiredWei,
    type: 2,
    maxPriorityFeePerGas,
    maxFeePerGas,
    gasLimit: 21000,
  };

  // Transfer tx (+20% gas safety)
  const tx2 = {
    to: ENS_BASE_REGISTRAR,
    data: txTransfer.data,
    type: 2,
    maxPriorityFeePerGas,
    maxFeePerGas,
    gasLimit: gasEstimateTransfer.mul(12).div(10),
  };

  const bundle = [
    { signer: funder,      transaction: txFund },
    { signer: compromised, transaction: tx2   },
  ];

  console.log("Preparing Flashbots private bundle…");
  console.table({
    label: NAME,
    tokenId: TOKEN_ID.toString(),
    owner: compromised.address,
    newOwner,
    gasEstimateTransfer: gasEstimateTransfer.toString(),
    maxFeePerGasGwei: Number(ethers.utils.formatUnits(maxFeePerGas, "gwei")),
    maxPriorityGwei: Number(ethers.utils.formatUnits(maxPriorityFeePerGas, "gwei")),
    fundAmountEth: ethers.utils.formatEther(requiredWei),
    retryBlocks: RETRY_BLOCKS,
  });

  // First attempt
  let targetBlock = (await provider.getBlockNumber()) + 1;
  let resp = await flashbots.sendBundle(bundle, targetBlock);
  await assertSimulation(resp);

  // Wait result & retry loop
  let result = await resp.wait();
  if (result === 0) {
    console.log("✅ Bundle included on first attempt!");
    return;
  }

  console.warn("⏳ Not included in first target block; retrying…");
  for (let i = 0; i < RETRY_BLOCKS; i++) {
    targetBlock = (await provider.getBlockNumber()) + 1;
    resp = await flashbots.sendBundle(bundle, targetBlock);
    const waited = await resp.wait();
    if (waited === 0) {
      console.log(`✅ Bundle included on retry #${i + 1}!`);
      return;
    }
  }

  console.error("❌ Bundle not included after retries. Raise MAX_PRIORITY_GWEI or FEE_MULTIPLIER.");
  process.exit(2);
}

// ======= helpers =======
function env(k) {
  const v = process.env[k];
  if (!v) throw new Error(`Missing env: ${k}`);
  return v;
}

function assertV5() {
  // ethers v5 identifies as something like 'ethers/5.7.2'
  const v = String(ethers.version || "");
  if (!v.includes("5.")) {
    throw new Error(
      `This script requires ethers v5. Detected: ${v}. Run:\n  npm remove ethers\n  npm i ethers@5 @flashbots/ethers-provider-bundle@0.6.4 dotenv@16`
    );
  }
}

async function assertSimulation(resp) {
  const sim = await resp.simulate();
  if ("error" in sim) {
    console.error("Simulation error:", sim.error);
    process.exit(1);
  } else {
    console.log("Simulation OK:", {
      coinbaseDiffEth: ethers.utils.formatEther(sim.coinbaseDiff),
      totalGasUsed: sim.totalGasUsed.toString(),
    });
  }
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
