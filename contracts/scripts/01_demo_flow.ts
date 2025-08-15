import pkg from 'hardhat';
const { ethers } = pkg;

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
