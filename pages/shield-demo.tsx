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
