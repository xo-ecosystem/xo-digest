Absolutely—let’s tie your Shield Aether stack to a Piggy NFT that’s (a) cute/memey, (b) pitch-ready, and (c) actually useful.

Below is a drop-in NFT that:
	•	Renders on-chain SVG (a piggy with live stats) — no IPFS needed.
	•	Points at your live Vault + sAETH and shows current vault ETH & backing per sAETH in the image and metadata.
	•	Is free-mint (demo) with a supply cap you choose.
	•	Safe by default: it doesn’t move funds; it’s a badge/pass that visualizes backing. (We can later add drip/points/boosts or claim mechanics.)

⸻

1) Contract: PiggyNFT.sol

Add to contracts/PiggyNFT.sol:

// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/Strings.sol";
import "@openzeppelin/contracts/utils/Base64.sol";

interface IShieldVault {
    function balance() external view returns (uint256);
}

interface IShieldAether {
    function totalSupply() external view returns (uint256);
    function backingPerToken_wei1e18() external view returns (uint256);
}

contract PiggyNFT is ERC721, Ownable {
    using Strings for uint256;

    IShieldVault public immutable vault;
    IShieldAether public immutable saeth;
    uint256 public immutable maxSupply;
    uint256 public totalMinted;

    event Minted(address indexed to, uint256 indexed tokenId);

    constructor(
        address _vault,
        address _saeth,
        uint256 _maxSupply,
        address _owner
    ) ERC721("Piggy Bank Shield (Demo)", "PIGGY") Ownable(_owner) {
        require(_vault != address(0) && _saeth != address(0), "zero addr");
        vault = IShieldVault(_vault);
        saeth = IShieldAether(_saeth);
        maxSupply = _maxSupply;
    }

    function mint(address to) external onlyOwner returns (uint256 tokenId) {
        require(totalMinted < maxSupply, "sold out");
        tokenId = ++totalMinted;
        _safeMint(to, tokenId);
        emit Minted(to, tokenId);
    }

    // ------- Metadata (on-chain, dynamic) -------

    function tokenURI(uint256 tokenId) public view override returns (string memory) {
        require(_ownerOf(tokenId) != address(0), "not minted");

        uint256 vaultEth = address(vault).balance; // same as vault.balance(), cheaper view
        uint256 supply = saeth.totalSupply();
        uint256 backingWei1e18 = saeth.backingPerToken_wei1e18();

        string memory vaultEthStr = _toEthStr(vaultEth);
        string memory supplyStr = _toEthStr(supply); // 18 decimals
        string memory backingStr = _toEthStr(backingWei1e18); // wei per token scaled 1e18 => ETH per 1 sAETH

        // minimal cute SVG (dark bg + pig + numbers)
        string memory svg = string(abi.encodePacked(
            '<svg xmlns="http://www.w3.org/2000/svg" width="1024" height="1024">',
            '<rect width="100%" height="100%" fill="#0B1020"/>',
            '<g transform="translate(80,80)">',
              '<text x="0" y="40" fill="#F5F7FF" font-family="monospace" font-size="36">Piggy Bank Shield</text>',
              '<text x="0" y="90" fill="#9FB3FF" font-family="monospace" font-size="24">Token #', tokenId.toString(), '</text>',
              // pig body
              '<g transform="translate(0,140)">',
                '<ellipse cx="240" cy="180" rx="220" ry="150" fill="#FF7AB6"/>',
                '<circle cx="420" cy="160" r="40" fill="#FF8FC1"/>',
                '<circle cx="160" cy="150" r="15" fill="#2D0A2C"/>',
                '<ellipse cx="280" cy="200" rx="46" ry="32" fill="#FFC2DA"/>',
                '<circle cx="260" cy="200" r="10" fill="#C94090"/>',
                '<circle cx="300" cy="200" r="10" fill="#C94090"/>',
                '<rect x="180" y="70" width="120" height="10" rx="5" fill="#1F2A4C"/>',
              '</g>',
              // stats box
              '<g transform="translate(520,130)">',
                '<rect width="380" height="300" rx="16" fill="#131A33" stroke="#2C3B73" stroke-width="2"/>',
                '<text x="20" y="50" fill="#CFE0FF" font-family="monospace" font-size="22">Vault ETH: ', vaultEthStr, '</text>',
                '<text x="20" y="100" fill="#CFE0FF" font-family="monospace" font-size="22">sAETH Supply: ', supplyStr, '</text>',
                '<text x="20" y="150" fill="#CFE0FF" font-family="monospace" font-size="22">Backing/1 sAETH: ', backingStr, '</text>',
                '<text x="20" y="220" fill="#90EE90" font-family="monospace" font-size="18">Live, on-chain stats.</text>',
              '</g>',
            '</g>',
            '</svg>'
        ));

        string memory json = string(abi.encodePacked(
            '{"name":"Piggy Bank Shield #', tokenId.toString(), '",',
            '"description":"A cute on-chain pass reflecting live Shield Aether vault stats. Demo only.",',
            '"attributes":[',
              '{"trait_type":"Vault ETH","value":"', vaultEthStr, '"},',
              '{"trait_type":"sAETH Supply","value":"', supplyStr, '"},',
              '{"trait_type":"Backing/1 sAETH","value":"', backingStr, '"}',
            '],',
            '"image":"data:image/svg+xml;base64,', Base64.encode(bytes(svg)), '"}'
        ));

        return string(abi.encodePacked(
            "data:application/json;base64,", Base64.encode(bytes(json))
        ));
    }

    // Format 18-dec numbers to ETH string with 4 decimals (rough prettifier)
    function _toEthStr(uint256 weiOrWei1e18) internal pure returns (string memory) {
        // everything we pass is effectively 18-dec scaled
        uint256 whole = weiOrWei1e18 / 1e18;
        uint256 frac = (weiOrWei1e18 % 1e18) / 1e14; // 4 decimals
        // pad 4 decimals
        bytes memory f = bytes(Strings.toString(frac));
        if (frac < 1000) f = abi.encodePacked(bytes4("0000"), f); // naive pad, ok for demo
        return string(abi.encodePacked(Strings.toString(whole), ".", _right4(f)));
    }
    function _right4(bytes memory b) private pure returns (bytes memory out) {
        // return last 4 bytes of decimal buffer
        uint256 L = b.length;
        if (L >= 4) {
            out = new bytes(4);
            out[0]=b[L-4]; out[1]=b[L-3]; out[2]=b[L-2]; out[3]=b[L-1];
        } else {
            out = "0000";
        }
    }
}

What it does
	•	Owner-gated mint(to) (easy to airdrop allowlist/founders/holders).
	•	tokenURI() pulls live numbers from your vault & sAETH and renders an SVG pig + stats.

⸻

2) Wire into your deploy script

Edit scripts/00_deploy.ts to deploy + optionally mint a batch:

// after you deployed ShieldVault, ShieldAether, SeasonalMemecoin, MiniAMM…
const Piggy = await ethers.getContractFactory("PiggyNFT");
const piggy = await Piggy.deploy(vaultAddr, sAAddr, /*maxSupply=*/ 777, deployer.address);
await piggy.waitForDeployment();
const piggyAddr = await piggy.getAddress();
console.log("PiggyNFT:", piggyAddr);

// demo airdrop 3 passes
await (await piggy.mint(deployer.address)).wait();
await (await piggy.mint(deployer.address)).wait();
await (await piggy.mint(deployer.address)).wait();

Remember to rebuild then redeploy:

npm run build
npm run deploy


⸻

3) Minimal UI: show owned Piggies + live image

In your Next app, add a tiny viewer pages/piggy.tsx:

import { useEffect, useMemo, useState } from "react";
import { BrowserProvider, Contract, JsonRpcSigner } from "ethers";

const ADDR = {
  PIGGY: process.env.NEXT_PUBLIC_PIGGY!,
};

const ABI = [
  "function totalMinted() view returns (uint256)",
  "function maxSupply() view returns (uint256)",
  "function ownerOf(uint256) view returns (address)",
  "function tokenURI(uint256) view returns (string)",
];

export default function PiggyPage() {
  const [provider, setProvider] = useState<BrowserProvider>();
  const [signer, setSigner] = useState<JsonRpcSigner>();
  const [addr, setAddr] = useState<string>();
  const [owned, setOwned] = useState<number[]>([]);
  const [uris, setUris] = useState<Record<number,string>>({});

  const piggy = useMemo(()=> provider && new Contract(ADDR.PIGGY, ABI, signer || provider), [provider, signer]);

  useEffect(() => {
    if (typeof window === "undefined" || !("ethereum" in window)) return;
    setProvider(new BrowserProvider((window as any).ethereum));
  }, []);

  async function connect() {
    if (!provider) return;
    const s = await provider.getSigner();
    setSigner(s);
    setAddr(await s.getAddress());
  }

  async function refresh() {
    if (!piggy || !addr) return;
    const tm = Number(await piggy.totalMinted());
    const mine: number[] = [];
    for (let id=1; id<=tm; id++) {
      try {
        const o = await piggy.ownerOf(id);
        if (o.toLowerCase() === addr.toLowerCase()) mine.push(id);
      } catch {}
    }
    setOwned(mine);
    const out: Record<number,string> = {};
    await Promise.all(mine.map(async (id) => { out[id] = await piggy.tokenURI(id); }));
    setUris(out);
  }

  return (
    <div style={{maxWidth:960, margin:"40px auto", fontFamily:"ui-sans-serif"}}>
      <h1>🐷 Piggy Bank Shield — Your Passes</h1>
      <div style={{display:"flex", gap:8}}>
        <button onClick={connect}>Connect</button>
        <button onClick={refresh} disabled={!addr}>Refresh</button>
      </div>
      {addr && <p>Connected: <b>{addr}</b></p>}
      <div style={{display:"grid", gridTemplateColumns:"repeat(auto-fill, minmax(320px,1fr))", gap:16, marginTop:16}}>
        {owned.map(id => (
          <div key={id} style={{border:"1px solid #223", borderRadius:12, overflow:"hidden"}}>
            <div style={{padding:12}}><b>Token #{id}</b></div>
            {uris[id] && (
              <img src={JSON.parse(atob(uris[id].split(",")[1])).image} alt={`Piggy #${id}`} />
            )}
          </div>
        ))}
        {owned.length === 0 && <p>No Piggies yet. (Owner/airdrop only in demo)</p>}
      </div>
      <p style={{opacity:.7, marginTop:16}}>
        Image + stats render on-chain; reload to see live vault/sAETH changes.
      </p>
    </div>
  );
}

Add to .env.local:

NEXT_PUBLIC_PIGGY=0x...   # address from deploy logs


⸻

Where this fits in your pitch
	•	Narrative: Piggy NFT is the fan pass that visually proves there’s real backing and a working flywheel (fees → AMM → vault). It’s meme-native and data-rich.
	•	Utility hooks to add later (options):
	•	Holder-only boosts or lower rate limits on /publish.
	•	Allowlist for special mints or “feed the pig” keeper rewards.
	•	Soft-staking → XP that increases “oink power” shown on the SVG.
	•	Redeem-boost coupons (e.g., 0.5% fee rebate when triggering convertFees keeper calls).

If you want, I can:
	•	Add a keeper reward for convertFees() and a Piggy-holder boost.
	•	Gate /ops/broadcast test endpoint by Piggy ownership for fun internal demos.
	•	Add a free-mint window (e.g., first N wallets per drop), then switch to paid mint.

Want me to ship those tweaks as follow-ups?
