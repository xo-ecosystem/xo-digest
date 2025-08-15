Awesome—here’s a single, paste-ready “Apply All” prompt for Cursor that bundles everything: contracts (Piggy + keeper reward), backend Piggy-gated ops route, the tiny Next.js demo page, and env scaffolding. It’s organized with Files filter + Create/Update blocks so Cursor can write the files cleanly.

⸻

🔧 Cursor “Apply All” Prompt — Piggy Demo Pack (Base Sepolia)

Files filter:
	•	contracts/PiggyNFT.sol
	•	contracts/MiniAMM.sol
	•	scripts/deploy/Piggy.deploy.ts
	•	src/xo_core/eth/piggy_check.py
	•	src/xo_core/routes/ops.py
	•	pages/piggy-demo.tsx
	•	.env (backend)
	•	.env.local (frontend)
	•	README.md (append)

Assumes Hardhat + OpenZeppelin for contracts, FastAPI backend under src/xo_core, and a Next.js frontend (same monorepo or adjacent). Adjust paths if your layout differs.

⸻

1) Contracts

1A) contracts/PiggyNFT.sol (new)

// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/Strings.sol";
import "@openzeppelin/contracts/utils/Base64.sol";

interface IShieldAether {
    function totalSupply() external view returns (uint256);
    function backingPerToken_wei1e18() external view returns (uint256);
}
interface IShieldVault { /* marker */ }

contract PiggyNFT is ERC721, Ownable {
    using Strings for uint256;

    IShieldVault public immutable vault;
    IShieldAether public immutable saeth;

    uint256 public immutable maxSupply;
    uint256 public totalMinted;

    // Free window → then paid
    uint256 public freeMintsRemaining;     // e.g. 333
    uint256 public publicPriceWei;         // e.g. 0.0002 ETH
    address public payout;                 // where paid mints go

    event Minted(address indexed to, uint256 indexed tokenId, uint256 pricePaid);

    constructor(
        address _vault,
        address _saeth,
        uint256 _maxSupply,
        uint256 _freeMints,
        uint256 _publicPriceWei,
        address _payout,
        address _owner
    ) ERC721("Piggy Bank Shield (Demo)", "PIGGY") Ownable(_owner) {
        require(_vault != address(0) && _saeth != address(0), "zero addr");
        vault = IShieldVault(_vault);
        saeth = IShieldAether(_saeth);
        maxSupply = _maxSupply;
        freeMintsRemaining = _freeMints;
        publicPriceWei = _publicPriceWei;
        payout = _payout;
    }

    // --- Admin controls ---
    function setPublicPrice(uint256 weiPrice) external onlyOwner { publicPriceWei = weiPrice; }
    function setPayout(address to) external onlyOwner { payout = to; }

    // --- Owner airdrop (no cost) ---
    function mint(address to) external onlyOwner returns (uint256 tokenId) {
        tokenId = _mintCore(to, 0);
    }

    // --- Public mint: free window then paid ---
    function mintPublic() external payable returns (uint256 tokenId) {
        uint256 price = 0;
        if (freeMintsRemaining > 0) {
            freeMintsRemaining -= 1;
        } else {
            price = publicPriceWei;
            require(msg.value == price, "bad price");
        }
        tokenId = _mintCore(msg.sender, price);
        if (price > 0 && payout != address(0)) {
            (bool ok,) = payout.call{value: price}("");
            require(ok, "payout fail");
        }
    }

    function _mintCore(address to, uint256 pricePaid) internal returns (uint256 tokenId) {
        require(totalMinted < maxSupply, "sold out");
        tokenId = ++totalMinted;
        _safeMint(to, tokenId);
        emit Minted(to, tokenId, pricePaid);
    }

    // ------- Metadata (on-chain SVG, live stats) -------
    function tokenURI(uint256 tokenId) public view override returns (string memory) {
        require(_ownerOf(tokenId) != address(0), "not minted");

        uint256 vaultEth = address(vault).balance;
        uint256 supply = saeth.totalSupply();
        uint256 backingWei1e18 = saeth.backingPerToken_wei1e18();

        string memory vaultEthStr = _toEthStr(vaultEth);
        string memory supplyStr = _toEthStr(supply);
        string memory backingStr = _toEthStr(backingWei1e18);

        string memory svg = string(abi.encodePacked(
            '<svg xmlns="http://www.w3.org/2000/svg" width="1024" height="1024">',
            '<rect width="100%" height="100%" fill="#0B1020"/>',
            '<g transform="translate(80,80)">',
              '<text x="0" y="40" fill="#F5F7FF" font-family="monospace" font-size="36">Piggy Bank Shield</text>',
              '<text x="0" y="90" fill="#9FB3FF" font-family="monospace" font-size="24">Token #', tokenId.toString(), '</text>',
              '<g transform="translate(0,140)">',
                '<ellipse cx="240" cy="180" rx="220" ry="150" fill="#FF7AB6"/>',
                '<circle cx="420" cy="160" r="40" fill="#FF8FC1"/>',
                '<circle cx="160" cy="150" r="15" fill="#2D0A2C"/>',
                '<ellipse cx="280" cy="200" rx="46" ry="32" fill="#FFC2DA"/>',
                '<circle cx="260" cy="200" r="10" fill="#C94090"/>',
                '<circle cx="300" cy="200" r="10" fill="#C94090"/>',
                '<rect x="180" y="70" width="120" height="10" rx="5" fill="#1F2A4C"/>',
              '</g>',
              '<g transform="translate(520,130)">',
                '<rect width="380" height="300" rx="16" fill="#131A33" stroke="#2C3B73" stroke-width="2"/>',
                '<text x="20" y="50" fill="#CFE0FF" font-family="monospace" font-size="22">Vault ETH: ', vaultEthStr, '</text>',
                '<text x="20" y="100" fill="#CFE0FF" font-family="monospace" font-size="22">sAETH Supply: ', supplyStr, '</text>',
                '<text x="20" y="150" fill="#CFE0FF" font-family="monospace" font-size="22">Backing/1 sAETH: ', backingStr, '</text>',
              '</g>',
            '</g>',
            '</svg>'
        ));

        string memory json = string(abi.encodePacked(
            '{"name":"Piggy Bank Shield #', tokenId.toString(), '",',
            '"description":"On-chain pass reflecting Shield Aether vault stats. Demo.",',
            '"attributes":[',
              '{"trait_type":"Vault ETH","value":"', vaultEthStr, '"},',
              '{"trait_type":"sAETH Supply","value":"', supplyStr, '"},',
              '{"trait_type":"Backing/1 sAETH","value":"', backingStr, '"}',
            '],',
            '"image":"data:image/svg+xml;base64,', Base64.encode(bytes(svg)), '"}'
        ));
        return string(abi.encodePacked("data:application/json;base64,", Base64.encode(bytes(json))));
    }

    // Pretty 18-dec string (4 dp)
    function _toEthStr(uint256 n) internal pure returns (string memory) {
        uint256 whole = n / 1e18;
        uint256 frac = (n % 1e18) / 1e14; // 4 dp
        bytes memory f = bytes(Strings.toString(frac));
        while (f.length < 4) f = abi.encodePacked(bytes1("0"), f);
        return string(abi.encodePacked(Strings.toString(whole), ".", f));
    }

    receive() external payable {}
}

1B) contracts/MiniAMM.sol (new or patched)

// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/token/ERC721/IERC721.sol";

// Demo-grade: treats received ETH as "fees"; convertFees() splits to keeper+vault
contract MiniAMM is Ownable {
    IERC721 public piggy;               // Piggy NFT
    address payable public vault;       // Vault receiver

    uint256 public keeperRewardBps = 50;  // 0.50%
    uint256 public piggyBoostBps   = 25;  // +0.25% if holder
    uint256 public constant BPS    = 10_000;

    event FeesConverted(address indexed keeper, uint256 totalFees, uint256 rewardPaid, uint256 toVault);
    event ParamsUpdated(address piggy, address vault, uint256 keeperRewardBps, uint256 piggyBoostBps);

    constructor(address _owner) Ownable(_owner) {}

    function setParams(address piggyNft, address payable vaultAddr, uint256 rewardBps, uint256 boostBps) external onlyOwner {
        require(rewardBps <= 300 && boostBps <= 200, "too high");
        piggy = IERC721(piggyNft);
        vault = vaultAddr;
        keeperRewardBps = rewardBps;
        piggyBoostBps = boostBps;
        emit ParamsUpdated(piggyNft, vaultAddr, rewardBps, boostBps);
    }

    function convertFees() external {
        uint256 feesEth = address(this).balance;
        require(feesEth > 0, "no fees");
        uint256 bps = keeperRewardBps;

        if (address(piggy) != address(0)) {
            try piggy.balanceOf(msg.sender) returns (uint256 bal) {
                if (bal > 0) { bps += piggyBoostBps; }
            } catch {}
        }

        uint256 reward = (feesEth * bps) / BPS;
        uint256 toVault = feesEth - reward;

        (bool ok1,) = msg.sender.call{value: reward}("");
        require(ok1, "keeper pay fail");

        (bool ok2,) = vault.call{value: toVault}("");
        require(ok2, "vault pay fail");

        emit FeesConverted(msg.sender, feesEth, reward, toVault);
    }

    receive() external payable {}
}


⸻

2) Deploy helper

scripts/deploy/Piggy.deploy.ts (new)

import { ethers } from "hardhat";

async function main() {
  const [deployer] = await ethers.getSigners();
  console.log("Deployer:", deployer.address);

  // TODO: wire real addresses
  const VAULT_ADDR = process.env.VAULT_ADDR!;       // payable vault
  const SAETH_ADDR = process.env.SAETH_ADDR!;       // Shield Aether token (demo iface)
  if (!VAULT_ADDR || !SAETH_ADDR) throw new Error("Missing VAULT_ADDR/SAETH_ADDR");

  const Piggy = await ethers.getContractFactory("PiggyNFT");
  const piggy = await Piggy.deploy(
    VAULT_ADDR, SAETH_ADDR,
    /*maxSupply*/ 777,
    /*freeMints*/ 333,
    /*publicPriceWei*/ ethers.parseEther("0.0002"),
    /*payout*/ deployer.address,
    /*owner*/ deployer.address
  );
  await piggy.waitForDeployment();
  console.log("PiggyNFT:", await piggy.getAddress());

  const Mini = await ethers.getContractFactory("MiniAMM");
  const mini = await Mini.deploy(deployer.address);
  await mini.waitForDeployment();
  console.log("MiniAMM:", await mini.getAddress());

  // Keeper params: 0.50% + 0.25% boost
  const tx = await mini.setParams(await piggy.getAddress(), VAULT_ADDR, 50, 25);
  await tx.wait();
  console.log("MiniAMM params set.");
}

main().catch((e) => { console.error(e); process.exit(1); });


⸻

3) Backend: Piggy-gated ops endpoint

3A) src/xo_core/eth/piggy_check.py (new)

from web3 import Web3
from functools import lru_cache
import os
import time

RPC = os.getenv("BASE_RPC_URL")
PIGGY = os.getenv("PIGGY_NFT_ADDRESS")
if not (RPC and PIGGY):
    raise RuntimeError("Missing BASE_RPC_URL or PIGGY_NFT_ADDRESS")

W3 = Web3(Web3.HTTPProvider(RPC))
PIGGY_ADDR = Web3.to_checksum_address(PIGGY)

ABI = [{
    "constant": True, "inputs":[{"name":"owner","type":"address"}],
    "name":"balanceOf","outputs":[{"name":"","type":"uint256"}],"type":"function"
}]

@lru_cache(maxsize=1024)
def piggy_balance(addr: str, bucket: int = 0) -> int:
    # bucket: 30s cache window
    contract = W3.eth.contract(address=PIGGY_ADDR, abi=ABI)
    if not Web3.is_address(addr): return 0
    checksum = Web3.to_checksum_address(addr)
    # make cache key vary by 30-second windows
    now_bucket = int(time.time() // 30)
    _ = bucket or now_bucket
    return contract.functions.balanceOf(checksum).call()

3B) src/xo_core/routes/ops.py (update or create)

from fastapi import APIRouter, Header, HTTPException, Depends
from pydantic import BaseModel
from xo_core.eth.piggy_check import piggy_balance

router = APIRouter(prefix="/ops", tags=["ops"])

class BroadcastIn(BaseModel):
    topic: str
    payload: dict

def require_piggy(x_wallet: str = Header(..., alias="X-Wallet")):
    try:
        bal = piggy_balance(x_wallet)
    except Exception:
        raise HTTPException(status_code=500, detail="Piggy check failed")
    if bal == 0:
        raise HTTPException(status_code=403, detail="Piggy holder required")
    return x_wallet

@router.post("/broadcast")
def ops_broadcast(body: BroadcastIn, holder: str = Depends(require_piggy)):
    # TODO: wire your broadcaster here
    return {"ok": True, "relayed_by": holder, "topic": body.topic}

If you already have /ops/broadcast, just wrap it with require_piggy.

⸻

4) Frontend: tiny demo page

pages/piggy-demo.tsx (new)

import { useEffect, useState, useMemo } from "react";
import { BrowserProvider, Contract, formatEther, parseEther } from "ethers";

const ADDR = {
  PIGGY: process.env.NEXT_PUBLIC_PIGGY as string,
  FEES:  process.env.NEXT_PUBLIC_FEES as string, // MiniAMM
};
const PIGGY_ABI = [
  "function freeMintsRemaining() view returns (uint256)",
  "function publicPriceWei() view returns (uint256)",
  "function mintPublic() payable returns (uint256)",
  "function totalMinted() view returns (uint256)"
];
const FEES_ABI = ["function convertFees() payable"];

export default function Page() {
  const [provider, setProvider] = useState<BrowserProvider>();
  const [signer, setSigner] = useState<any>();
  const [addr, setAddr] = useState<string>("");

  const [freeLeft, setFreeLeft] = useState<number>(0);
  const [price, setPrice] = useState<string>("0");

  const piggy = useMemo(
    () => provider && ADDR.PIGGY && new Contract(ADDR.PIGGY, PIGGY_ABI, signer || provider),
    [provider, signer]
  );
  const fees = useMemo(
    () => provider && ADDR.FEES && new Contract(ADDR.FEES, FEES_ABI, signer || provider),
    [provider, signer]
  );

  useEffect(() => {
    if (typeof window !== "undefined" && (window as any).ethereum)
      setProvider(new BrowserProvider((window as any).ethereum));
  }, []);

  async function connect() {
    const s = await provider!.getSigner();
    setSigner(s);
    const a = await s.getAddress();
    setAddr(a);

    const [f, p] = await Promise.all([
      piggy!.freeMintsRemaining(),
      piggy!.publicPriceWei()
    ]);
    setFreeLeft(Number(f));
    setPrice(formatEther(p));
  }

  async function mintPiggy() {
    if (!piggy) return;
    const value = freeLeft > 0 ? 0n : parseEther(price);
    const tx = await piggy.mintPublic({ value });
    await tx.wait();
    await connect();
  }

  async function callConvertFees() {
    if (!fees) return;
    const tx = await fees.convertFees();
    await tx.wait();
    alert("convertFees() OK — keeper reward paid (Piggy gets boost).");
  }

  async function opsBroadcast() {
    const res = await fetch("/ops/broadcast", {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-Wallet": addr },
      body: JSON.stringify({ topic: "demo", payload: { t: Date.now() } })
    });
    if (res.status === 403) alert("Need a Piggy to use ops/broadcast.");
    else alert("Broadcast accepted.");
  }

  return (
    <div style={{maxWidth:720, margin:"40px auto", fontFamily:"ui-sans-serif"}}>
      <h1>🐷 Piggy Bank Shield — Demo</h1>
      {!addr ? <button onClick={connect} disabled={!provider}>Connect</button> : <p>Connected: <b>{addr}</b></p>}

      <div style={{marginTop:16, padding:12, border:"1px solid #223", borderRadius:12}}>
        <h3>Mint Piggy</h3>
        <p>Free mints remaining: <b>{freeLeft}</b></p>
        <p>Public price: <b>{price}</b> ETH</p>
        <button onClick={mintPiggy} disabled={!addr || !piggy}>Mint Piggy</button>
      </div>

      <div style={{marginTop:16, padding:12, border:"1px solid #223", borderRadius:12}}>
        <h3>Keeper Game</h3>
        <p>Call <code>convertFees()</code>; Piggy holders get a bonus.</p>
        <button onClick={callConvertFees} disabled={!addr || !fees}>convertFees()</button>
      </div>

      <div style={{marginTop:16, padding:12, border:"1px solid #223", borderRadius:12}}>
        <h3>Ops Broadcast (Piggy-gated)</h3>
        <button onClick={opsBroadcast} disabled={!addr}>POST /ops/broadcast</button>
      </div>
    </div>
  );
}


⸻

5) Environment

.env (backend)

BASE_RPC_URL=https://sepolia.base.org      # or your provider URL
PIGGY_NFT_ADDRESS=0xYourPiggyAddress

.env.local (frontend)

NEXT_PUBLIC_PIGGY=0xYourPiggyAddress
NEXT_PUBLIC_FEES=0xYourMiniAMMAddress


⸻

6) README.md (append near the top)

## Piggy Bank Shield — Demo (Base Sepolia)

**Contracts**
- PiggyNFT: `0x...`
- MiniAMM:  `0x...`  (keeper reward 0.50% + 0.25% Piggy boost)

**Backend**
- `/ops/broadcast` gated by Piggy ownership (header `X-Wallet`)

**Frontend**
- `/piggy-demo` page:
  - Mint Piggy (free window → paid)
  - Call `convertFees()` to receive keeper reward (boost with Piggy)
  - Test Piggy-gated `/ops/broadcast`

**Deploy**
```bash
# Contracts
VAULT_ADDR=0x... SAETH_ADDR=0x... npx hardhat run scripts/deploy/Piggy.deploy.ts --network baseSepolia
# Backend .env: BASE_RPC_URL, PIGGY_NFT_ADDRESS
# Frontend .env.local: NEXT_PUBLIC_PIGGY, NEXT_PUBLIC_FEES

Smoke tests

# Keeper: simulate contract receiving fees
cast send 0xMiniAMM --value 0.01ether           # deposit fees
# Keeper reward
cast send 0xMiniAMM "convertFees()" --from $EOA

# Ops (without Piggy → 403)
curl -i -X POST http://localhost:8000/ops/broadcast \
  -H 'Content-Type: application/json' \
  -H "X-Wallet: 0xNoPiggy" \
  -d '{"topic":"demo","payload":{"t":123}}'

# Ops (with Piggy → 200)
curl -i -X POST http://localhost:8000/ops/broadcast \
  -H 'Content-Type: application/json' \
  -H "X-Wallet: 0xHasPiggy" \
  -d '{"topic":"demo","payload":{"t":456}}'

---

## ✅ After Apply
1) **Compile & deploy** on Base Sepolia:
   - `VAULT_ADDR` (payable), `SAETH_ADDR` (demo iface ok)
   - Run `Piggy.deploy.ts` (prints Piggy + MiniAMM addresses)
2) Fill envs (backend+frontend) with those addresses.
3) Start backend (FastAPI) + frontend (Next.js).
4) Visit `/piggy-demo`, mint a free Piggy, then call `convertFees()` and test `/ops/broadcast`.

If you want this **wired into coalescent.lol** as a separate route with OIDC (Brie) auto-filling `X-Wallet`, I can drop a tiny session hook next.

Yep — breaking each large block into its own fresh Cursor chat will keep memory lean and prevent the “Cursor blow-up” crashes you’ve been seeing.

For the Piggy Bank Shield Aether + seasonal memecoin + live demo tokenomics, I’d split it like this so nothing gets lost:

Chat A — Contracts Layer
	•	SeasonalMemecoin mint-on-deploy tweak
	•	sAETH Shield Aether pegging logic + redeem rules
	•	Uniswap-v2-style router + pair (demo-grade)
	•	Piggy NFT contract with keeper reward + boost

Chat B — Backend Layer
	•	/ops/broadcast piggy-holder gating
	•	Vault-backing API endpoints
	•	Keeper reward triggers (convertFees() etc.)

Chat C — Frontend Layer
	•	Next.js page showing:
	•	Vault backing live
	•	sAETH supply + peg ratio
	•	Redeem box + Piggy holder bonuses
	•	Free-mint → paid-mint state switch

Chat D — Deployment Layer
	•	Deploy to Base Sepolia
	•	Seed vault with demo ETH + seasonal memecoin liquidity
	•	Run walkthrough with Brie login

If we do it in this order, we can keep each chat <30 prompts and avoid losing context while still stacking the whole MVP in 1–2 days.

Do you want me to prep Chat A — Contracts Layer first so we can ship the on-chain pieces before the UI?
