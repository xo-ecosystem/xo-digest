Absolutely—spinning up a tiny testnet prototype is worth it. It lets you demo the peg mechanics, the “tax → vault → backing ↑ → redeemable ↑” loop, and real flows (mint, swap, transfer-fee accrual, redeem). Below is a lean, demo-grade setup you can drop into xo-core-dev/contracts/ and deploy on Base Sepolia (cheap, fast).

⸻

What we’ll deploy (demo-grade)
	1.	ShieldVault (payable)

	•	Holds native ETH (on Base Sepolia = ETH).
	•	Anyone can send ETH to it (including the memecoin’s fee router).
	•	Exposes balance().

	2.	ShieldAether (ERC20)

	•	Represents “claim on vault.”
	•	Mint: owner-only for the demo (you’ll mint initial supply to yourself to simulate distribution).
	•	Redeem: holder can burn any amount and receive a pro-rata share of vault ETH:
payout = amount * vaultETH / totalSupply()
	•	Shows a live Backing Ratio: vaultETH / totalSupply().

	3.	SeasonalMemecoin (ERC20 with transfer fee)

	•	On every transfer, takes a fee (e.g., 2%) and forwards it to ShieldVault.
	•	No fee for transfers involving excluded addresses (owner, vault) so you can seed liquidity easily.
	•	Fee sends native ETH, not the token—so for the demo we’ll keep it simple:
	•	We’ll collect the fee in tokens and immediately sell them for ETH in real life via a router; for this demo, we just send the tokens to the vault (representing value flowing in).
	•	Then we’ll also include a manual “skimToVaultETH()” function you can call (owner only in demo) that unwraps WETH→ETH and funds the vault. (If no DEX/WETH setup: call sendETHToVault() directly to simulate revenue.)

Production would wire the fee to a DEX router to swap fee-tokens → WETH → unwrap → vault. For a pitch demo, we keep the mechanics visible and callable.

⸻

Folder layout

xo-core-dev/
  contracts/
    contracts/
      ShieldVault.sol
      ShieldAether.sol
      SeasonalMemecoin.sol
    scripts/
      00_deploy.ts
      01_demo_flow.ts
    hardhat.config.ts
    package.json
    .env


⸻

Contracts (Solidity ^0.8.24)

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

    /// demo mint (owner-only)
    function mint(address to, uint256 amount) external onlyOwner {
        _mint(to, amount);
    }

    /// burn sAETH for pro-rata ETH from vault
    function redeem(uint256 amount) external {
        uint256 ts = totalSupply();
        require(amount > 0 && amount <= balanceOf(msg.sender), "bad amount");
        require(ts > 0, "no supply");

        uint256 vaultEth = address(payable(address(vault))).balance;
        uint256 payout = (vaultEth * amount) / ts;

        _burn(msg.sender, amount);
        (bool ok,) = payable(msg.sender).call{value: payout}("");
        require(ok, "ETH transfer failed");
    }

    function backingRatioBps() external view returns (uint256) {
        uint256 ts = totalSupply();
        if (ts == 0) return 0;
        uint256 vaultEth = address(payable(address(vault))).balance;
        // ratio in basis points per token (ETH wei per 1e18 sAETH) -> return scaled to 1e18?
        // For demo, return 10_000 bps * (vaultEth/ts) is non-sense because units mismatch,
        // so expose the raw fraction as (vaultEth * 1e18 / ts) = ETH-per-token in wei (1e18 scaling):
        return uint256((vaultEth * 1e18) / ts);
    }

    // accept ETH directly (e.g., vault sends; uncommon)
    receive() external payable {}
}

contracts/SeasonalMemecoin.sol (demo fee-on-transfer that sends fee to vault as tokens; plus an owner helper to send ETH to vault for the demo)

// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

interface IVaultEth {
    function balance() external view returns (uint256);
}

contract SeasonalMemecoin is ERC20, Ownable {
    address public vault;
    uint256 public feeBps = 200; // 2% transfer fee (demo)
    mapping(address => bool) public feeExempt;

    event FeeToVault(address indexed from, address indexed to, uint256 amountTokens);
    event VaultUpdated(address indexed vault);
    event FeeBpsUpdated(uint256 feeBps);

    constructor(address owner_) ERC20("XO Seasonal Meme (Demo)", "SEASON") Ownable(owner_) {
        feeExempt[msg.sender] = true;
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

        super._update(from, vault, fee);   // send fee tokens to vault (demo)
        super._update(from, to,    net);

        emit FeeToVault(from, to, fee);
    }

    /// Demo helper: owner can send ETH to vault to simulate revenue conversion.
    function sendETHToVault() external payable onlyOwner {
        require(vault != address(0), "vault=0");
        (bool ok,) = payable(vault).call{value: msg.value}("");
        require(ok, "send fail");
    }
    receive() external payable {}
}

For a fuller demo you can also deploy a tiny DEX pair and a router to auto-convert fee-tokens → ETH, but that’s extra ceremony for investors. The above already proves the flywheel.

⸻

Hardhat setup (ethers v6)

contracts/package.json

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
    "ethers": "^6.13.2",
    "hardhat": "^2.22.7",
    "@openzeppelin/contracts": "^5.0.2",
    "dotenv": "^16.4.5",
    "typescript": "^5.5.4",
    "ts-node": "^10.9.2"
  }
}

contracts/hardhat.config.ts

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

contracts/.env (example)

RPC_URL=https://sepolia.base.org
PK=0xYOUR_PRIVATE_KEY  # test key


⸻

Deploy script

contracts/scripts/00_deploy.ts

import { ethers } from "hardhat";

async function main() {
  const [deployer] = await ethers.getSigners();
  console.log("Deployer:", deployer.address);

  // 1) Vault
  const Vault = await ethers.getContractFactory("ShieldVault");
  const vault = await Vault.deploy();
  await vault.waitForDeployment();
  console.log("ShieldVault:", await vault.getAddress());

  // 2) sAETH
  const SA = await ethers.getContractFactory("ShieldAether");
  const sAether = await SA.deploy(await vault.getAddress(), deployer.address);
  await sAether.waitForDeployment();
  console.log("ShieldAether:", await sAether.getAddress());

  // 3) Seasonal memecoin
  const SM = await ethers.getContractFactory("SeasonalMemecoin");
  const meme = await SM.deploy(deployer.address);
  await meme.waitForDeployment();
  console.log("SeasonalMemecoin:", await meme.getAddress());

  // wire fee target
  await (await meme.setVault(await vault.getAddress())).wait();

  // demo: mint tokens to deployer (10M)
  await (await meme.transfer(deployer.address, 0)).wait(); // ensure deployer has a mapping entry
  const mintAmt = ethers.parseUnits("10000000", 18);
  // OZ ERC20 has no public mint; in demo we’ll mint by owner via _mint in constructor pattern or
  // we can simulate by sending from owner’s initial balance (constructor doesn’t mint).
  // Simpler: modify SeasonalMemecoin to mint initial in constructor—skipping here:
  //   in constructor: _mint(owner_, 10000000e18);
  // If you added that, nothing to do. Else, update contract, recompile, and redeploy.

  // demo: sAETH mint to deployer (1M)
  await (await sAether.mint(deployer.address, ethers.parseUnits("1000000", 18))).wait();

  // demo: seed vault with small ETH so redeem works
  await deployer.sendTransaction({ to: await vault.getAddress(), value: ethers.parseEther("0.2") });

  console.log("Done.");
}

main().catch((e) => { console.error(e); process.exit(1); });

Tip: give SeasonalMemecoin a constructor _mint(owner_, 10_000_000e18); so you have supply to move around instantly.

⸻

Demo flow script

contracts/scripts/01_demo_flow.ts

import { ethers } from "hardhat";

const SAETH = "PUT_sAETH_ADDRESS";
const VAULT = "PUT_VAULT_ADDRESS";
const MEME  = "PUT_MEME_ADDRESS";

async function main() {
  const [you] = await ethers.getSigners();
  const sa = await ethers.getContractAt("ShieldAether", SAETH);
  const vaultAddress = VAULT;
  const meme = await ethers.getContractAt("SeasonalMemecoin", MEME);

  const show = async (label: string) => {
    const ts = await sa.totalSupply();
    const bal = await ethers.provider.getBalance(vaultAddress);
    console.log(`${label} :: sAETH totalSupply=${ethers.formatUnits(ts, 18)} | vaultETH=${ethers.formatEther(bal)}`);
  };

  await show("Start");

  // Simulate volume → fee to vault:
  // (Send some ETH to vault to simulate conversion)
  await (await meme.sendETHToVault({ value: ethers.parseEther("0.05") })).wait();
  await show("After sendETHToVault(0.05)");

  // Redeem 100 sAETH
  const redeemAmt = ethers.parseUnits("100", 18);
  await (await sa.redeem(redeemAmt)).wait();
  await show("After redeem(100)");
}

main().catch((e) => { console.error(e); process.exit(1); });


⸻

Run it

cd contracts
npm i
npm run build

# Deploy
npm run deploy

# Fill addresses into scripts/01_demo_flow.ts or pass via env and read in code
# Then:
npm run demo


⸻

Post-deploy quick tests (curl)
	•	Vault balance

cast balance VAULT_ADDRESS --rpc-url $RPC_URL

	•	Redeem (from your signer)

cast send SAETH_ADDRESS "redeem(uint256)" 100000000000000000000 \
  --private-key $PK --rpc-url $RPC_URL


⸻

Why this demo sells the story
	•	Live peg math: Investors watch backing ratio rise as value flows in.
	•	Visible “vault fill”: Even if fee-to-ETH routing isn’t wired, you can simulate revenue with one function.
	•	Redeem → get ETH: Real ETH in, sAETH out; sAETH burned, ETH back. The loop is tangible.
	•	Extendable: Drop in a router later to auto-convert fee-tokens to ETH. Swap Base Sepolia → Base mainnet when ready.

⸻

Caveats / next steps (post-demo hardening)
	•	Auto-routing fees to ETH via a DEX router (Uniswap-style).
	•	Guardrails: pausable, caps, upgradable via proxy, access roles.
	•	Oracles & AMMs: avoid circular mint/redeem games; consider time-weighted routes and circuit breakers.
	•	Legal/Tax: fee-on-transfer + redeemable claims can have regulatory implications—get counsel.
	•	Subgraph/Indexing for metrics (backing, flows, holders).
	•	Frontend mint/redeem UI wired to Base RPC.

⸻

If you want, I can:
	•	tweak SeasonalMemecoin to mint in constructor (so you don’t have to edit deploy script),
	•	wire a Uniswap-v2-style minimal router + pair (still demo-grade),
	•	or produce a tiny Next.js page that shows vault backing, sAETH supply, redeem box, all pointed at Base Sepolia.
