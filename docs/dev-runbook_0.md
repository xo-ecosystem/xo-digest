Perfect—here’s a compact, copy-pasteable pack you can drop into a new Cursor Agent chat. It gives you:
	•	✅ SeasonalMemecoin that mints in the constructor and batches fee → ETH → ShieldVault via a tiny AMM
	•	✅ A minimal Uniswap-v2-style AMM (constant-product) for demo routing
	•	✅ A tiny Next.js demo page that shows vault backing, sAETH supply, and a redeem box (Base Sepolia)

⸻

0) Create the Hardhat workspace

mkdir -p contracts/{contracts,scripts} && cd contracts
npm init -y
npm i -D hardhat @nomicfoundation/hardhat-toolbox @nomicfoundation/hardhat-ethers ethers dotenv typescript ts-node @openzeppelin/contracts
npx hardhat --yes

package.json (replace scripts)

{
  "name": "xo-contracts-demo",
  "private": true,
  "type": "module",
  "scripts": {
    "build": "hardhat compile",
    "deploy": "hardhat run scripts/00_deploy.ts --network baseSepolia",
    "demo": "hardhat run scripts/01_demo_flow.ts --network baseSepolia"
  },
  "devDependencies": {
    "@nomicfoundation/hardhat-ethers": "^3.0.5",
    "@nomicfoundation/hardhat-toolbox": "^5.0.0",
    "@openzeppelin/contracts": "^5.0.2",
    "dotenv": "^16.4.5",
    "ethers": "^6.13.2",
    "hardhat": "^2.22.7",
    "ts-node": "^10.9.2",
    "typescript": "^5.5.4"
  }
}

hardhat.config.ts

import { HardhatUserConfig } from "hardhat/config";
import "@nomicfoundation/hardhat-toolbox";
import * as dotenv from "dotenv";
dotenv.config();

const config: HardhatUserConfig = {
  solidity: "0.8.24",
  networks: {
    baseSepolia: {
      url: process.env.RPC_URL || "https://sepolia.base.org",
      accounts: process.env.PK ? [process.env.PK] : []
    }
  }
};
export default config;

.env (example)

RPC_URL=https://sepolia.base.org
PK=0xYOUR_TEST_PRIVATE_KEY


⸻

1) Contracts

contracts/ShieldVault.sol

// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

contract ShieldVault {
    event Received(address indexed from, uint256 amount);
    receive() external payable { emit Received(msg.sender, msg.value); }

    function balance() external view returns (uint256) {
        return address(this).balance;
    }
}

contracts/ShieldAether.sol

// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

interface IVault {
    function balance() external view returns (uint256);
}

contract ShieldAether is ERC20, Ownable {
    IVault public immutable vault;

    constructor(address vault_, address owner_) ERC20("Shield Aether (Demo)", "sAETH") Ownable(owner_) {
        require(vault_ != address(0), "vault=0");
        vault = IVault(vault_);
    }

    function mint(address to, uint256 amount) external onlyOwner {
        _mint(to, amount);
    }

    function redeem(uint256 amount) external {
        uint256 ts = totalSupply();
        require(ts > 0 && amount > 0, "bad amount");
        uint256 payout = (address(payable(address(vault))).balance * amount) / ts;
        _burn(msg.sender, amount);
        (bool ok,) = payable(msg.sender).call{value: payout}("");
        require(ok, "ETH transfer failed");
    }

    /// ETH (wei) backing per 1e18 sAETH, scaled by 1e18
    function backingPerToken_wei1e18() external view returns (uint256) {
        uint256 ts = totalSupply();
        if (ts == 0) return 0;
        return (address(payable(address(vault))).balance * 1e18) / ts;
    }

    receive() external payable {}
}

contracts/MiniAMM.sol (constant-product demo AMM, Token↔ETH)

// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

contract MiniAMM {
    IERC20 public immutable token;
    uint112 public reserveToken; // token reserve
    uint112 public reserveETH;   // ETH reserve (in wei)
    uint32  public blockTimestampLast;

    event Sync(uint112 reserveToken, uint112 reserveETH);
    event AddLiquidity(address indexed provider, uint256 tokenIn, uint256 ethIn);
    event SwapT2E(address indexed caller, uint256 tokenIn, uint256 ethOut, address to);
    event SwapE2T(address indexed caller, uint256 ethIn, uint256 tokenOut, address to);

    constructor(address token_) { token = IERC20(token_); }

    function _update(uint256 balToken, uint256 balETH) internal {
        reserveToken = uint112(balToken);
        reserveETH   = uint112(balETH);
        blockTimestampLast = uint32(block.timestamp);
        emit Sync(reserveToken, reserveETH);
    }

    function sync() public {
        _update(token.balanceOf(address(this)), address(this).balance);
    }

    function addLiquidity(uint256 tokenAmount) external payable {
        require(tokenAmount > 0 && msg.value > 0, "bad liq");
        require(token.transferFrom(msg.sender, address(this), tokenAmount), "t xfer fail");
        _update(token.balanceOf(address(this)), address(this).balance);
        emit AddLiquidity(msg.sender, tokenAmount, msg.value);
    }

    function _getOut(uint256 amtIn, uint256 resIn, uint256 resOut) internal pure returns (uint256) {
        // 0.3% fee
        uint256 amtInWithFee = amtIn * 997;
        return (amtInWithFee * resOut) / (resIn * 1000 + amtInWithFee);
    }

    function swapTokensForETH(uint256 tokenIn, uint256 minEthOut, address to) external {
        require(token.transferFrom(msg.sender, address(this), tokenIn), "t xferFrom fail");
        uint256 ethOut = _getOut(tokenIn, reserveToken, reserveETH);
        require(ethOut >= minEthOut, "slippage");
        (bool ok,) = payable(to).call{value: ethOut}("");
        require(ok, "eth xfer fail");
        _update(token.balanceOf(address(this)), address(this).balance);
        emit SwapT2E(msg.sender, tokenIn, ethOut, to);
    }

    function swapETHForTokens(uint256 minTokenOut, address to) external payable {
        uint256 tokenOut = _getOut(msg.value, reserveETH, reserveToken);
        require(tokenOut >= minTokenOut, "slippage");
        require(token.transfer(to, tokenOut), "t xfer fail");
        _update(token.balanceOf(address(this)), address(this).balance);
        emit SwapE2T(msg.sender, msg.value, tokenOut, to);
    }

    receive() external payable {}
}

contracts/SeasonalMemecoin.sol (constructor mint + fee accumulation + batch convert → ETH → Vault)

// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

interface IMiniAMM {
    function swapTokensForETH(uint256 tokenIn, uint256 minEthOut, address to) external;
}

contract SeasonalMemecoin is ERC20, Ownable {
    address public vault;
    uint256 public feeBps = 200; // 2%
    mapping(address => bool) public feeExempt;
    uint256 public accumulatedFees; // tokens sitting in this contract

    event VaultUpdated(address indexed vault);
    event FeeBpsUpdated(uint256 feeBps);
    event FeesConverted(uint256 tokenSold, uint256 minEthOut, address to);

    constructor(address owner_) ERC20("XO Seasonal Meme (Demo)", "SEASON") Ownable(owner_) {
        feeExempt[msg.sender] = true;
        _mint(owner_, 10_000_000e18); // demo supply
    }

    function setVault(address v) external onlyOwner { vault = v; emit VaultUpdated(v); }
    function setFeeBps(uint256 bps) external onlyOwner { require(bps <= 1000, "fee>10%"); feeBps = bps; emit FeeBpsUpdated(bps); }
    function setFeeExempt(address a, bool ex) external onlyOwner { feeExempt[a] = ex; }

    function _update(address from, address to, uint256 value) internal override {
        if (value == 0 || feeExempt[from] || feeExempt[to] || vault == address(0)) {
            super._update(from, to, value);
            return;
        }
        uint256 fee = (value * feeBps) / 10_000;
        uint256 net = value - fee;

        // collect fee into this contract to batch-convert later
        super._update(from, address(this), fee);
        super._update(from, to, net);

        accumulatedFees += fee;
    }

    /// Approve AMM to pull from *this* contract when converting fees
    function approveAMM(address amm) external onlyOwner {
        _approve(address(this), amm, type(uint256).max);
    }

    /// Convert accumulated fee tokens to ETH via AMM and forward ETH to vault
    function convertFees(address amm, uint256 tokenAmount, uint256 minEthOut) external onlyOwner {
        require(vault != address(0), "vault=0");
        require(tokenAmount > 0 && tokenAmount <= accumulatedFees, "bad amount");
        accumulatedFees -= tokenAmount;
        IMiniAMM(amm).swapTokensForETH(tokenAmount, minEthOut, vault);
        emit FeesConverted(tokenAmount, minEthOut, vault);
    }

    receive() external payable {}
}


⸻

2) Deployment + demo scripts

scripts/00_deploy.ts

import { ethers } from "hardhat";

async function main() {
  const [deployer] = await ethers.getSigners();
  console.log("Deployer:", deployer.address);

  // Vault
  const Vault = await ethers.getContractFactory("ShieldVault");
  const vault = await Vault.deploy();
  await vault.waitForDeployment();
  const vaultAddr = await vault.getAddress();
  console.log("ShieldVault:", vaultAddr);

  // sAETH
  const SA = await ethers.getContractFactory("ShieldAether");
  const sAether = await SA.deploy(vaultAddr, deployer.address);
  await sAether.waitForDeployment();
  const sAAddr = await sAether.getAddress();
  console.log("ShieldAether:", sAAddr);

  // Meme
  const SM = await ethers.getContractFactory("SeasonalMemecoin");
  const meme = await SM.deploy(deployer.address);
  await meme.waitForDeployment();
  const memeAddr = await meme.getAddress();
  console.log("SeasonalMemecoin:", memeAddr);

  // Wire vault + mint demo sAETH + seed vault
  await (await meme.setVault(vaultAddr)).wait();
  await (await sAether.mint(deployer.address, ethers.parseUnits("1000000", 18))).wait();
  await deployer.sendTransaction({ to: vaultAddr, value: ethers.parseEther("0.1") });

  // AMM
  const AMM = await ethers.getContractFactory("MiniAMM");
  const amm = await AMM.deploy(memeAddr);
  await amm.waitForDeployment();
  const ammAddr = await amm.getAddress();
  console.log("MiniAMM:", ammAddr);

  // Approvals & add liquidity (100k tokens : 1 ETH)
  await (await meme.approve(ammAddr, ethers.MaxUint256)).wait();
  await (await meme.approveAMM(ammAddr)).wait();
  await (await amm.addLiquidity(ethers.parseUnits("100000", 18), { value: ethers.parseEther("1") })).wait();

  // Show initial
  const vaultBal = await ethers.provider.getBalance(vaultAddr);
  console.log("Vault ETH (initial):", ethers.formatEther(vaultBal));
  console.log("Done.");
}

main().catch((e) => { console.error(e); process.exit(1); });

scripts/01_demo_flow.ts

import { ethers } from "hardhat";

const ADDR = {
  VAULT: "PUT_VAULT",
  SAETH: "PUT_SAETH",
  MEME : "PUT_MEME",
  AMM  : "PUT_AMM"
};

async function main() {
  const [you, alice] = await ethers.getSigners();
  const sa = await ethers.getContractAt("ShieldAether", ADDR.SAETH);
  const meme = await ethers.getContractAt("SeasonalMemecoin", ADDR.MEME);

  const show = async (label: string) => {
    const ts = await sa.totalSupply();
    const bal = await ethers.provider.getBalance(ADDR.VAULT);
    console.log(`${label} :: sAETH=${ethers.formatUnits(ts,18)} | vaultETH=${ethers.formatEther(bal)}`);
  };

  await show("Start");

  // Generate fees: send 10k MEME to Alice (2% fee accumulates in contract)
  await (await meme.transfer(alice.address, ethers.parseUnits("10000", 18))).wait();

  // Convert some accumulated fee tokens → ETH → Vault
  await (await meme.convertFees(ADDR.AMM, ethers.parseUnits("100", 18), 0)).wait();

  await show("After convertFees(100)");

  // Redeem 100 sAETH (from you)
  await (await sa.redeem(ethers.parseUnits("100",18))).wait();
  await show("After redeem(100)");
}

main().catch((e)=>{ console.error(e); process.exit(1); });

Run:

npm run build
npm run deploy
# paste addresses into 01_demo_flow.ts
npm run demo


⸻

3) Tiny Next.js page (Base Sepolia)

From your project root (not contracts):

npm i ethers

Create pages/shield-demo.tsx (or app/shield-demo/page.tsx if using App Router):

// pages/shield-demo.tsx
import { useEffect, useMemo, useState } from "react";
import { BrowserProvider, Contract, formatEther, formatUnits, JsonRpcSigner } from "ethers";

const ADDR = {
  VAULT: process.env.NEXT_PUBLIC_VAULT!,
  SAETH: process.env.NEXT_PUBLIC_SAETH!,
  MEME : process.env.NEXT_PUBLIC_MEME!,
  AMM  : process.env.NEXT_PUBLIC_AMM!,
};
const CHAIN_ID = 84532; // Base Sepolia

const SAETH_ABI = [
  "function totalSupply() view returns (uint256)",
  "function redeem(uint256 amount) external",
  "function backingPerToken_wei1e18() view returns (uint256)",
];

const VAULT_ABI = ["function balance() view returns (uint256)"];

export default function ShieldDemo() {
  const [provider, setProvider] = useState<BrowserProvider>();
  const [signer, setSigner] = useState<JsonRpcSigner>();
  const [addr, setAddr] = useState<string>();
  const [vaultEth, setVaultEth] = useState<string>("0");
  const [supply, setSupply] = useState<string>("0");
  const [backing, setBacking] = useState<string>("0");

  const sa = useMemo(()=> provider && new Contract(ADDR.SAETH, SAETH_ABI, signer || provider), [provider, signer]);
  const vault = useMemo(()=> provider && new Contract(ADDR.VAULT, VAULT_ABI, provider), [provider]);

  useEffect(() => {
    if (typeof window === "undefined" || !("ethereum" in window)) return;
    const p = new BrowserProvider((window as any).ethereum);
    setProvider(p);
  }, []);

  async function connect() {
    if (!provider) return;
    await (window as any).ethereum.request({ method: "wallet_addEthereumChain", params: [{
      chainId: "0x14A34", chainName: "Base Sepolia", nativeCurrency: { name: "ETH", symbol: "ETH", decimals: 18 },
      rpcUrls: ["https://sepolia.base.org"], blockExplorerUrls: ["https://sepolia.basescan.org"]
    }]});
    const s = await provider.getSigner();
    setSigner(s);
    setAddr(await s.getAddress());
  }

  async function refresh() {
    if (!provider || !sa || !vault) return;
    const v = await vault.balance();
    const ts = await sa.totalSupply();
    const br = await sa.backingPerToken_wei1e18();
    setVaultEth(formatEther(v));
    setSupply(formatUnits(ts, 18));
    // br is wei-per-token scaled 1e18 => display in ETH per token
    setBacking(formatEther(br));
  }

  async function redeemHundred() {
    if (!signer || !sa) return;
    const tx = await sa.connect(signer).redeem(BigInt(100) * 10n ** 18n);
    await tx.wait();
    await refresh();
    alert("Redeemed 100 sAETH");
  }

  return (
    <div style={{maxWidth: 720, margin: "40px auto", fontFamily: "ui-sans-serif,system-ui"}}>
      <h1>Shield Aether Demo (Base Sepolia)</h1>
      <button onClick={connect} style={{padding:8, borderRadius:8}}>{addr ? `Connected: ${addr.slice(0,6)}…` : "Connect"}</button>
      <button onClick={refresh} style={{padding:8, marginLeft: 8, borderRadius:8}}>Refresh</button>
      <div style={{marginTop:16}}>
        <div>Vault ETH: <b>{vaultEth}</b></div>
        <div>sAETH Supply: <b>{supply}</b></div>
        <div>Backing per 1 sAETH (ETH): <b>{backing}</b></div>
      </div>
      <hr />
      <h3>Redeem</h3>
      <button onClick={redeemHundred} style={{padding:8, borderRadius:8}}>Redeem 100 sAETH</button>
      <p style={{opacity:.7, marginTop:8}}>Use the deployer wallet for demo; holders can redeem pro-rata from vault.</p>
      <hr />
      <small>
        VAULT: {ADDR.VAULT}<br/>
        sAETH: {ADDR.SAETH}<br/>
        MEME: {ADDR.MEME}<br/>
        AMM: {ADDR.AMM}
      </small>
    </div>
  );
}

.env.local for Next.js

NEXT_PUBLIC_VAULT=0x...
NEXT_PUBLIC_SAETH=0x...
NEXT_PUBLIC_MEME=0x...
NEXT_PUBLIC_AMM=0x...

Run:

npm run dev
# open http://localhost:3000/shield-demo


⸻

Quick “does it work?” checklist
	•	npm run deploy prints ShieldVault, ShieldAether, SeasonalMemecoin, MiniAMM addresses.
	•	Liquidity added (100k MEME : 1 ETH).
	•	npm run demo shows Vault ETH increasing after convertFees.
	•	Next.js page shows live Vault ETH, sAETH supply, Backing per token and lets you redeem 100 sAETH.

⸻

Notes / next polish
	•	The AMM is intentionally tiny. For more realism, we can swap in full UniV2 Factory+Router, point fees through Router, and unwrap WETH→ETH to vault automatically.
	•	convertFees is owner-only for the demo; in production you may make it public with a keeper reward and MEV-safe guards.
	•	Add RBAC/Pausable, circuit breakers, and tests before mainnet.

If you want, I can also supply:
	•	a Uniswap-V2 Factory + Router deploy script wired to WETH for Base Sepolia,
	•	or a hardhat task suite (npx hardhat convertFees --amm ... --amount ...) for quick operator ops.
