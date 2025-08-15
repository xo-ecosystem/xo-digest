Heck yes—perfect demo flow for coalescent.lol. Below are tight, paste-ready upgrades to make the showcase sing:
	•	Keeper reward on convertFees() (+ Piggy-holder boost)
	•	Gate /ops/broadcast by Piggy NFT ownership
	•	Free-mint window → paid mint for Piggy NFT
	•	Minimal UI hooks + env you’ll need

⸻

1) Contracts

1A) PiggyNFT: add free-mint window + paid mint

Replace your PiggyNFT.sol with this backward-compatible superset (keeps mint(owner) for airdrops):

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
    address public payout;                 // where paid mints go (e.g. vault/ops)

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

Deploy tweak (TypeScript):

const Piggy = await ethers.getContractFactory("PiggyNFT");
const piggy = await Piggy.deploy(
  vaultAddr, sAAddr,
  /*maxSupply*/ 777,
  /*freeMints*/ 333,
  /*publicPriceWei*/ ethers.parseEther("0.0002"),
  /*payout*/ deployer.address, // or vault
  deployer.address
);
await piggy.waitForDeployment();
console.log("PiggyNFT:", await piggy.getAddress());


⸻

1B) MiniAMM (or your fees contract): keeper reward + Piggy boost

Add a lightweight keeper reward when someone calls convertFees(). If the caller holds a PiggyNFT, they get a boost.

Patch in your AMM/fees contract (names may differ—adjust):

// add at top
import "@openzeppelin/contracts/token/ERC721/IERC721.sol";

contract MiniAMM {
    // ...
    IERC721 public piggy;               // Piggy NFT address
    uint256 public keeperRewardBps = 50;      // 0.50% base of fees processed
    uint256 public piggyBoostBps   = 25;      // +0.25% if caller holds Piggy
    uint256 public constant BPS = 10_000;

    function setKeeperParams(address piggyNft, uint256 rewardBps, uint256 boostBps) external onlyOwner {
        require(rewardBps <= 300 && boostBps <= 200, "too high");
        piggy = IERC721(piggyNft);
        keeperRewardBps = rewardBps;
        piggyBoostBps = boostBps;
    }

    // Example convertFees() — replace "feesEth" with your actual flows
    function convertFees() external {
        uint256 feesEth = address(this).balance; // demo: using contract ETH
        require(feesEth > 0, "no fees");

        uint256 bps = keeperRewardBps;
        if (address(piggy) != address(0)) {
            // Cheap check: does caller own ANY Piggy?
            // NOTE: ERC721 doesn't expose balanceOf in interface? It does. Use IERC721.
            try piggy.balanceOf(msg.sender) returns (uint256 bal) {
                if (bal > 0) { bps += piggyBoostBps; }
            } catch {}
        }

        uint256 reward = (feesEth * bps) / BPS;
        uint256 toVault = feesEth - reward;

        // Payout keeper
        (bool ok1,) = msg.sender.call{value: reward}("");
        require(ok1, "keeper pay fail");

        // Send remainder to vault or do your swap/peg logic here
        (bool ok2,) = vault.call{value: toVault}("");
        require(ok2, "vault pay fail");

        emit FeesConverted(msg.sender, feesEth, reward, toVault);
    }

    event FeesConverted(address indexed keeper, uint256 totalFees, uint256 rewardPaid, uint256 sentToVault);

    address payable public vault;
    function setVault(address payable v) external onlyOwner { vault = v; }

    receive() external payable {}
}

Result
	•	Any wallet can call convertFees().
	•	They get a small reward, boosted if they hold Piggy.
	•	Great for showing “keeper game” in the demo.

⸻

2) Backend: gate /ops/broadcast by Piggy ownership

Add a quick wallet → Piggy balance check using Base Sepolia RPC in your FastAPI app.

2A) Config

.env (backend):

BASE_RPC_URL=...           # Base Sepolia RPC
PIGGY_NFT_ADDRESS=0x...    # from deployment

2B) Utility

src/xo_core/eth/piggy_check.py:

from web3 import Web3
from functools import lru_cache
import os
import time

RPC = os.getenv("BASE_RPC_URL")
PIGGY = Web3.to_checksum_address(os.getenv("PIGGY_NFT_ADDRESS"))
W3 = Web3(Web3.HTTPProvider(RPC))

ABI = [{
    "constant": True, "inputs":[{"name":"owner","type":"address"}],
    "name":"balanceOf","outputs":[{"name":"","type":"uint256"}],"type":"function"
}]

@lru_cache(maxsize=1024)
def _cache_key(addr: str, bucket: int) -> int:
    return int(bucket)

def piggy_balance(addr: str) -> int:
    if not Web3.is_address(addr): return 0
    contract = W3.eth.contract(address=PIGGY, abi=ABI)
    # 30s cache bucket
    bucket = int(time.time() // 30)
    _cache_key(addr.lower(), bucket)  # prime cache
    return contract.functions.balanceOf(Web3.to_checksum_address(addr)).call()

2C) Route gate

src/xo_core/routes/ops.py (or wherever /ops/broadcast lives):

from fastapi import APIRouter, Header, HTTPException, Depends
from pydantic import BaseModel
from xo_core.eth.piggy_check import piggy_balance

router = APIRouter(prefix="/ops", tags=["ops"])

class BroadcastIn(BaseModel):
    topic: str
    payload: dict

def require_piggy(xo_wallet_address: str = Header(..., alias="X-Wallet")):
    # Brie’s frontend sends the connected EOA in X-Wallet header
    if piggy_balance(xo_wallet_address) == 0:
        raise HTTPException(status_code=403, detail="Piggy holder required")
    return xo_wallet_address

@router.post("/broadcast")
def ops_broadcast(body: BroadcastIn, _holder=Depends(require_piggy)):
    # …call your broadcaster…
    return {"ok": True, "relayed_by": _holder}

Client side: when Brie is logged in, pass her EOA as X-Wallet header (your OIDC session knows it).

⸻

3) Frontend tweaks (Next.js)

3A) Piggy mint (free→paid) + keeper call

pages/piggy-demo.tsx (tiny demo):

import { useEffect, useState, useMemo } from "react";
import { BrowserProvider, Contract, formatEther, parseEther } from "ethers";

const ADDR = {
  PIGGY: process.env.NEXT_PUBLIC_PIGGY!,
  FEES:  process.env.NEXT_PUBLIC_FEES!, // MiniAMM / fees contract with convertFees()
};

const PIGGY_ABI = [
  "function freeMintsRemaining() view returns (uint256)",
  "function publicPriceWei() view returns (uint256)",
  "function mintPublic() payable returns (uint256)",
  "function totalMinted() view returns (uint256)"
];

const FEES_ABI = [
  "function convertFees() payable"
];

export default function Page() {
  const [provider, setProvider] = useState<BrowserProvider>();
  const [signer, setSigner] = useState<any>();
  const [addr, setAddr] = useState<string>("");

  const [freeLeft, setFreeLeft] = useState<number>(0);
  const [price, setPrice] = useState<string>("0");

  const piggy = useMemo(()=> provider && new Contract(ADDR.PIGGY, PIGGY_ABI, signer || provider), [provider, signer]);
  const fees  = useMemo(()=> provider && new Contract(ADDR.FEES,  FEES_ABI,  signer || provider), [provider, signer]);

  useEffect(() => { if (typeof window !== "undefined" && (window as any).ethereum) setProvider(new BrowserProvider((window as any).ethereum)); }, []);

  async function connect() {
    const s = await provider!.getSigner();
    setSigner(s);
    setAddr(await s.getAddress());
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
    await connect(); // refresh counters
  }

  async function callConvertFees() {
    if (!fees) return;
    const tx = await fees.convertFees(); // reward goes to msg.sender (you)
    await tx.wait();
    alert("convertFees() called — keeper reward paid (Piggy gets boost)!");
  }

  return (
    <div style={{maxWidth:720, margin:"40px auto", fontFamily:"ui-sans-serif"}}>
      <h1>🐷 Piggy Bank Shield — Demo</h1>
      {!addr ? <button onClick={connect}>Connect</button> : <p>Connected: <b>{addr}</b></p>}
      <div style={{marginTop:16, padding:12, border:"1px solid #223", borderRadius:12}}>
        <p>Free mints remaining: <b>{freeLeft}</b></p>
        <p>Public price: <b>{price}</b> ETH</p>
        <button onClick={mintPiggy} disabled={!addr}>Mint Piggy</button>
      </div>

      <div style={{marginTop:16, padding:12, border:"1px solid #223", borderRadius:12}}>
        <h3>Keeper Game</h3>
        <p>Call <code>convertFees()</code>. If you hold a Piggy, you get a bonus.</p>
        <button onClick={callConvertFees} disabled={!addr}>convertFees()</button>
      </div>
    </div>
  );
}

.env.local (frontend):

NEXT_PUBLIC_PIGGY=0x...
NEXT_PUBLIC_FEES=0x...


⸻

4) Coalescent.lol demo checklist
	1.	Deploy to Base Sepolia: Vault, sAETH, MiniAMM (fees), PiggyNFT
	•	Set setKeeperParams(piggy, 50, 25) → 0.50% base + 0.25% Piggy boost
	•	Set MiniAMM.setVault(vault)
	2.	Frontend (Vercel or your host) on coalescent.lol:
	•	pages/piggy-demo.tsx and your existing tokenomics view
	•	OIDC (Brie login) → read EOA → send as X-Wallet header to /ops/broadcast
	3.	Backend (FastAPI):
	•	RPC + PIGGY_NFT_ADDRESS env set
	•	/ops/broadcast gated by Piggy ownership (header X-Wallet)
	•	Optional: show keeper reward events in /message-bottle/stream for fun

⸻

Optional polish (fast wins)
	•	UI badge: “Piggy Holder ✅ Boost +0.25%” when wallet owns Piggy.
	•	Leaderboard: Top 10 keepers by fees converted (read events).
	•	Allow Piggy-holders to access a /redeem preview (no execution, just math).

⸻

If you drop me the deployed addresses for (Vault, sAETH, MiniAMM, Piggy) on Base Sepolia, I’ll give you a one-shot env block + exact curl smoke tests:
	•	mint free Piggy
	•	mint paid Piggy
	•	call convertFees() and see reward delta with/without Piggy
	•	hit /ops/broadcast with and without Piggy to see 403 → 200 flip

Want me to bundle these patches into a single Cursor “Apply All” prompt next?
