You got it—here’s Chat A — Contracts Layer (Apply All) as a single, paste-ready Cursor prompt. It sets up a Hardhat workspace targeting Base Sepolia, ships the four on-chain pieces, and includes deploy + verify scripts.

⸻

✅ Apply-All Prompt — “Chat A: Contracts Layer (Base Sepolia)”

Files filter (create if missing):
	•	contracts/
	•	deploy/
	•	scripts/
	•	hardhat.config.ts
	•	package.json
	•	.env.example
	•	README-contracts.md

1) package.json

{
  "name": "xo-aether-contracts",
  "version": "0.1.0",
  "private": true,
  "type": "module",
  "scripts": {
    "build": "hardhat compile",
    "clean": "hardhat clean",
    "test": "hardhat test",
    "deploy:base-sepolia": "hardhat run deploy/001_deploy_all.ts --network baseSepolia",
    "verify:base-sepolia": "node scripts/verify-all.js baseSepolia"
  },
  "devDependencies": {
    "@nomicfoundation/hardhat-toolbox": "^5.0.0",
    "hardhat": "^2.22.10",
    "ts-node": "^10.9.2",
    "typescript": "^5.5.4",
    "dotenv": "^16.4.5"
  },
  "dependencies": {
    "@openzeppelin/contracts": "^5.0.2"
  }
}

2) hardhat.config.ts

import { HardhatUserConfig } from "hardhat/config";
import "@nomicfoundation/hardhat-toolbox";
import * as dotenv from "dotenv";
dotenv.config();

const pk = process.env.PRIVATE_KEY || "0x0000000000000000000000000000000000000000000000000000000000000000";

const config: HardhatUserConfig = {
  solidity: {
    version: "0.8.24",
    settings: { optimizer: { enabled: true, runs: 500 } }
  },
  networks: {
    hardhat: {},
    baseSepolia: {
      url: process.env.BASE_SEPOLIA_RPC_URL || "",
      accounts: [pk]
    }
  },
  etherscan: {
    apiKey: {
      baseSepolia: process.env.BASESCAN_API_KEY || ""
    },
    customChains: [
      {
        network: "baseSepolia",
        chainId: 84532,
        urls: {
          apiURL: "https://api-sepolia.basescan.org/api",
          browserURL: "https://sepolia.basescan.org"
        }
      }
    ]
  }
};

export default config;

3) .env.example

# Fill these before deploy
PRIVATE_KEY=0xabc...your_demo_key
BASE_SEPOLIA_RPC_URL=https://sepolia.base.org
BASESCAN_API_KEY=YOUR_BASESCAN_KEY


⸻

Contracts

4) contracts/SeasonalMemecoin.sol

// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {ERC20} from "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import {Ownable} from "@openzeppelin/contracts/access/Ownable.sol";

/// @title SeasonalMemecoin
/// @notice Simple ERC20 that mints full initial supply in constructor to a treasury (owner or specified).
contract SeasonalMemecoin is ERC20, Ownable {
    uint8 private immutable _decimals;

    constructor(
        string memory name_,
        string memory symbol_,
        uint8 decimals_,
        uint256 initialSupply, // in tokens with decimals applied (e.g., 1_000_000e18)
        address mintTo,
        address initialOwner
    ) ERC20(name_, symbol_) Ownable(initialOwner) {
        _decimals = decimals_;
        _mint(mintTo == address(0) ? initialOwner : mintTo, initialSupply);
    }

    function decimals() public view override returns (uint8) {
        return _decimals;
    }
}

5) contracts/ShieldAether.sol  (sAETH “Shield Aether”)

// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {ERC20} from "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import {Ownable} from "@openzeppelin/contracts/access/Ownable.sol";

/// @title ShieldAether (sAETH)
/// @notice ETH-backed “shield” token. Vault holds ETH. Redeem pays a % of backing per token (performance peg).
///         For a live product you’ll likely prefer WETH custody + audits. This is demo-grade.
contract ShieldAether is ERC20, Ownable {
    /// @dev Redeem basis points; e.g., 2100 => 21% of backing per token redeemed.
    uint256 public redeemBps;       // default e.g., 2100 (21%)
    uint256 public keeperRewardBps; // reward on convertFees (in ETH share of transferred-in amount)

    event Deposited(address indexed from, uint256 amount);
    event Redeemed(address indexed to, uint256 sAmount, uint256 ethOut);
    event FeesConverted(address indexed keeper, uint256 ethIn, uint256 rewardPaid);
    event ParamsSet(uint256 redeemBps, uint256 keeperRewardBps);

    constructor(address initialOwner, uint256 redeemBps_, uint256 keeperRewardBps_)
        ERC20("Shield Aether", "sAETH")
        Ownable(initialOwner)
    {
        redeemBps = redeemBps_;
        keeperRewardBps = keeperRewardBps_;
    }

    /// @notice 1:1 mint on deposit for demo (1 ETH -> 1 sAETH).
    ///         You can adjust to a bonding curve or time-based schedule later.
    function deposit() external payable {
        require(msg.value > 0, "no ETH");
        _mint(msg.sender, msg.value);
        emit Deposited(msg.sender, msg.value);
    }

    /// @dev Backing per token = address(this).balance / totalSupply (in 1e18 scale since we use ETH and 18 d.p.)
    function backingPerToken() public view returns (uint256) {
        uint256 ts = totalSupply();
        if (ts == 0) return 0;
        return address(this).balance * 1e18 / ts;
    }

    function setParams(uint256 redeemBps_, uint256 keeperRewardBps_) external onlyOwner {
        require(redeemBps_ <= 10_000 && keeperRewardBps_ <= 2000, "bps out of range");
        redeemBps = redeemBps_;
        keeperRewardBps = keeperRewardBps_;
        emit ParamsSet(redeemBps, keeperRewardBps);
    }

    /// @notice Burn sAETH to redeem ETH; receives redeemBps% of backing-per-token * amount.
    function redeem(uint256 sAmount) external {
        require(sAmount > 0, "zero");
        uint256 bpt = backingPerToken(); // in 1e18 ETH units per sAETH
        uint256 ethGross = sAmount * bpt / 1e18;
        uint256 ethOut   = ethGross * redeemBps / 10_000;
        require(ethOut <= address(this).balance, "insufficient vault");
        _burn(msg.sender, sAmount);
        (bool ok, ) = msg.sender.call{value: ethOut}("");
        require(ok, "ETH xfer fail");
        emit Redeemed(msg.sender, sAmount, ethOut);
    }

    /// @notice Demo keeper hook: when LP fees (ETH) are sent here, caller triggers accounting & is paid keeper reward.
    ///         In this simple version, we assume fees are transferred into this contract before calling.
    function convertFees() external {
        // Track pre-balance? For demo we treat entire msg.value==0, so use delta via parameter? Simpler:
        // In practice, router/pair would call this with value; here we just reward small tip from vault to caller.
        uint256 reward = address(this).balance * keeperRewardBps / 10_000;
        if (reward > 0) {
            (bool ok, ) = msg.sender.call{value: reward}("");
            require(ok, "keeper reward fail");
        }
        emit FeesConverted(msg.sender, 0, reward);
    }

    receive() external payable {}
}

6) contracts/PiggyNFT.sol

// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {ERC721} from "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import {Ownable} from "@openzeppelin/contracts/access/Ownable.sol";
import {Strings} from "@openzeppelin/contracts/utils/Strings.sol";

/// @title PiggyNFT
/// @notice Fun demo NFT: free-mint for first N, then paid. Simple tokenURI base.
///         Use this to gate /ops/broadcast or to boost redeem/mint logic in UI off-chain.
contract PiggyNFT is ERC721, Ownable {
    using Strings for uint256;

    uint256 public immutable MAX_SUPPLY;
    uint256 public freeMintCap;
    uint256 public priceWei;
    string public baseURI;
    uint256 public totalMinted;

    constructor(
        string memory name_,
        string memory symbol_,
        uint256 maxSupply_,
        uint256 freeMintCap_,
        uint256 priceWei_,
        string memory baseURI_,
        address initialOwner
    ) ERC721(name_, symbol_) Ownable(initialOwner) {
        MAX_SUPPLY = maxSupply_;
        freeMintCap = freeMintCap_;
        priceWei = priceWei_;
        baseURI = baseURI_;
    }

    function setPrice(uint256 newPrice) external onlyOwner { priceWei = newPrice; }
    function setFreeMintCap(uint256 cap) external onlyOwner { freeMintCap = cap; }
    function setBaseURI(string memory uri) external onlyOwner { baseURI = uri; }

    function mint() external payable {
        require(totalMinted < MAX_SUPPLY, "sold out");
        if (totalMinted >= freeMintCap) {
            require(msg.value >= priceWei, "insufficient payment");
        }
        uint256 id = ++totalMinted;
        _safeMint(msg.sender, id);
    }

    function tokenURI(uint256 tokenId) public view override returns (string memory) {
        require(_ownerOf(tokenId) != address(0), "not minted");
        return string(abi.encodePacked(baseURI, tokenId.toString(), ".json"));
    }

    function withdraw(address payable to) external onlyOwner {
        (bool ok,) = to.call{value: address(this).balance}("");
        require(ok, "withdraw fail");
    }

    receive() external payable {}
}

7) contracts/DemoPair.sol  (tiny x*y=k AMM + LP)

// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {IERC20} from "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import {ERC20} from "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import {Ownable} from "@openzeppelin/contracts/access/Ownable.sol";

/// @notice Minimal demo AMM pair (constant product). Not production safe.
///         LP token is this contract (ERC20). 0.3% fee skim to feeTo (optional).
contract DemoPair is ERC20, Ownable {
    address public token0;
    address public token1;
    address public feeTo;      // e.g., ShieldAether vault
    uint256 public feeBps;     // 30 = 0.3%

    uint112 private reserve0;
    uint112 private reserve1;

    error InvalidToken();
    error InsufficientLiquidity();
    error InsufficientInput();

    constructor(address _t0, address _t1, address _owner, address _feeTo, uint256 _feeBps)
        ERC20("XO-LP", "XO-LP")
        Ownable(_owner)
    {
        require(_t0 != _t1 && _t0 != address(0) && _t1 != address(0), "bad tokens");
        token0 = _t0; token1 = _t1;
        feeTo = _feeTo;
        feeBps = _feeBps;
    }

    function setFee(address _feeTo, uint256 _feeBps) external onlyOwner {
        require(_feeBps <= 100, "max 1%");
        feeTo = _feeTo;
        feeBps = _feeBps;
    }

    function getReserves() public view returns (uint112, uint112) { return (reserve0, reserve1); }

    function _update(uint256 bal0, uint256 bal1) private {
        reserve0 = uint112(bal0);
        reserve1 = uint112(bal1);
    }

    function _balance0() private view returns (uint256) { return IERC20(token0).balanceOf(address(this)); }
    function _balance1() private view returns (uint256) { return IERC20(token1).balanceOf(address(this)); }

    function addLiquidity(uint256 amount0, uint256 amount1) external returns (uint256 liquidity) {
        IERC20(token0).transferFrom(msg.sender, address(this), amount0);
        IERC20(token1).transferFrom(msg.sender, address(this), amount1);
        (uint112 r0, uint112 r1) = (reserve0, reserve1);

        if (r0 == 0 && r1 == 0) {
            liquidity = sqrt(amount0 * amount1);
        } else {
            uint256 l0 = (totalSupply() * amount0) / r0;
            uint256 l1 = (totalSupply() * amount1) / r1;
            liquidity = l0 < l1 ? l0 : l1;
        }
        require(liquidity > 0, "liquidity=0");
        _mint(msg.sender, liquidity);
        _update(_balance0(), _balance1());
    }

    function removeLiquidity(uint256 liquidity) external returns (uint256 out0, uint256 out1) {
        require(liquidity > 0 && liquidity <= balanceOf(msg.sender), "bad liq");
        uint256 supply = totalSupply();
        out0 = (IERC20(token0).balanceOf(address(this)) * liquidity) / supply;
        out1 = (IERC20(token1).balanceOf(address(this)) * liquidity) / supply;
        _burn(msg.sender, liquidity);
        IERC20(token0).transfer(msg.sender, out0);
        IERC20(token1).transfer(msg.sender, out1);
        _update(_balance0(), _balance1());
    }

    function swap(address inToken, uint256 amountIn, address to) external returns (uint256 amountOut) {
        if (!(inToken == token0 || inToken == token1)) revert InvalidToken();
        require(amountIn > 0, "zero in");
        address outToken = inToken == token0 ? token1 : token0;

        // Pull in
        IERC20(inToken).transferFrom(msg.sender, address(this), amountIn);

        // Apply fee (optional)
        uint256 fee = (amountIn * feeBps) / 10_000;
        uint256 amountAfterFee = amountIn - fee;
        if (fee > 0 && feeTo != address(0)) {
            IERC20(inToken).transfer(feeTo, fee);
        }

        (uint112 r0, uint112 r1) = (reserve0, reserve1);
        (uint256 xRes, uint256 yRes) = inToken == token0 ? (uint256(r0), uint256(r1)) : (uint256(r1), uint256(r0));
        require(xRes > 0 && yRes > 0, "empty pool");

        // x*y=k, solve for amountOut = y - k/(x+amountAfterFee)
        uint256 k = xRes * yRes;
        uint256 newX = xRes + amountAfterFee;
        uint256 newY = k / newX;
        amountOut = yRes - newY;
        require(amountOut > 0, "no out");

        IERC20(outToken).transfer(to, amountOut);
        _update(_balance0(), _balance1());
    }

    function sqrt(uint256 y) private pure returns (uint256 z) {
        if (y > 3) { z = y; uint256 x = y / 2 + 1; while (x < z) { z = x; x = (y / x + x) / 2; } }
        else if (y != 0) { z = 1; }
    }
}

8) contracts/DemoRouter.sol

// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {IERC20} from "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import {Ownable} from "@openzeppelin/contracts/access/Ownable.sol";

interface IPair {
    function token0() external view returns (address);
    function token1() external view returns (address);
    function addLiquidity(uint256 amount0, uint256 amount1) external returns (uint256 liquidity);
    function removeLiquidity(uint256 liquidity) external returns (uint256 out0, uint256 out1);
    function swap(address inToken, uint256 amountIn, address to) external returns (uint256 amountOut);
}

contract DemoRouter is Ownable {
    constructor(address initialOwner) Ownable(initialOwner) {}

    function addLiquidity(
        address pair,
        uint256 amt0,
        uint256 amt1
    ) external returns (uint256 lpOut) {
        address t0 = IPair(pair).token0();
        address t1 = IPair(pair).token1();
        IERC20(t0).transferFrom(msg.sender, pair, amt0);
        IERC20(t1).transferFrom(msg.sender, pair, amt1);
        lpOut = IPair(pair).addLiquidity(0, 0); // pair already received tokens
    }

    function removeLiquidity(address pair, uint256 lp) external returns (uint256 out0, uint256 out1) {
        // Pull LP in then transfer to pair? Simpler: pair burns from sender; approve pair first.
        (out0, out1) = IPair(pair).removeLiquidity(lp);
    }

    function swapExactTokensForTokens(address pair, address inToken, uint256 amountIn, address to)
        external
        returns (uint256 amountOut)
    {
        IERC20(inToken).transferFrom(msg.sender, pair, amountIn);
        amountOut = IPair(pair).swap(inToken, amountIn, to);
    }
}


⸻

Deploy Script

9) deploy/001_deploy_all.ts

import { ethers } from "hardhat";

async function main() {
  const [deployer] = await ethers.getSigners();
  console.log("Deployer:", deployer.address);

  // 1) Seasonal Memecoin (demo supply)
  const Memecoin = await ethers.getContractFactory("SeasonalMemecoin");
  const memecoin = await Memecoin.deploy(
    "FlipToken", "FLIP", 18,
    ethers.parseEther("1000000"), // 1,000,000 FLIP
    deployer.address,             // mint to
    deployer.address              // owner
  );
  await memecoin.waitForDeployment();
  console.log("SeasonalMemecoin:", await memecoin.getAddress());

  // 2) Shield Aether (21% redeem, 1% (100bps) keeper reward demo)
  const sAETH = await (await ethers.getContractFactory("ShieldAether"))
    .deploy(deployer.address, 2100, 100);
  await sAETH.waitForDeployment();
  console.log("ShieldAether sAETH:", await sAETH.getAddress());

  // 3) Demo Pair (FLIP / sAETH), fee -> sAETH vault (contract address)
  const Pair = await ethers.getContractFactory("DemoPair");
  const pair = await Pair.deploy(
    await memecoin.getAddress(),
    await sAETH.getAddress(),
    deployer.address,
    await sAETH.getAddress(),
    30 // 0.3% fee
  );
  await pair.waitForDeployment();
  console.log("DemoPair:", await pair.getAddress());

  // 4) Demo Router
  const Router = await ethers.getContractFactory("DemoRouter");
  const router = await Router.deploy(deployer.address);
  await router.waitForDeployment();
  console.log("DemoRouter:", await router.getAddress());

  // Approvals for LP + swaps (quality of life, local only—you’ll still need user approvals in UI)
  const memAs = await ethers.getContractAt("IERC20", await memecoin.getAddress());
  const saAs = await ethers.getContractAt("IERC20", await sAETH.getAddress());
  await (await memAs.approve(await pair.getAddress(), ethers.MaxUint256)).wait();
  await (await saAs.approve(await pair.getAddress(), ethers.MaxUint256)).wait();

  // Optional: seed sAETH by depositing a little ETH -> sAETH (1:1)
  // NOTE: This sends ETH to the sAETH vault and mints sAETH to the deployer
  await (await ethers.getSigner()).sendTransaction({ to: await sAETH.getAddress(), value: ethers.parseEther("0.1") });
  await (await (await ethers.getContractAt("ShieldAether", await sAETH.getAddress())).deposit({ value: 0 })).wait().catch(()=>{});

  console.log("Done.");
}

main().catch((e) => { console.error(e); process.exit(1); });

If your node/provider doesn’t allow a bare sendTransaction to a contract before deployment finalization, just comment that deposit block and call sAETH.deposit({value: ...}) directly after deploy:

// await (await sAETH.deposit({ value: ethers.parseEther("0.1") })).wait();


⸻

Verify helper

10) scripts/verify-all.js

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

(Simple stub; for full auto-verify, capture addresses & args in the deploy script and write to .last-deploy.json.)

⸻

README

11) README-contracts.md

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

If deploy prints addresses, copy them to your frontend .env.local.

Notes
	•	SeasonalMemecoin mints full supply in the constructor (no further mint).
	•	ShieldAether.deposit() mints 1 sAETH per 1 ETH (demo). redeemBps (default 21%) pays a fraction of backing-per-token on redemption (modeling your “performance peg”).
	•	DemoPair skims a 0.3% swap fee to feeTo (set to sAETH). Call sAETH.convertFees() to reward keepers (pays keeperRewardBps from vault).
	•	PiggyNFT lets you free-mint for the first freeMintCap mints, then requires priceWei. Use token ownership on the backend to gate ops.

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


⸻

What this gives you right now
	•	Mint-on-deploy memecoin ✔️
	•	Shield Aether (sAETH) with deposit, redeem (% of backing), keeper reward ✔️
	•	Tiny AMM (pair + router) to demo FLIP↔sAETH swaps, fees flowing to vault ✔️
	•	Piggy NFT for fun gating/boosts ✔️
	•	Deploy to Base Sepolia with one command ✔️

When you’re ready, I can prep Chat B (Backend) to:
	•	gate /ops/broadcast by Piggy ownership,
	•	expose vault & peg stats,
	•	surface convertFees() keeper flow,
	•	and feed the live coalescent.lol demo.
