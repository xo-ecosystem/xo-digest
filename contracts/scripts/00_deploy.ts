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

  // Piggy NFT (free-mint for first 100, then paid via priceWei; baseURI should point to your metadata endpoint)
  const Piggy = await ethers.getContractFactory("PiggyNFT");
  const piggy = await Piggy.deploy(
    "Piggy Bank Shield (Demo)",
    "PIGGY",
    /*maxSupply=*/ 777,
    /*freeMintCap=*/ 100,
    /*priceWei=*/ 0,
    /*baseURI=*/ "https://your-domain.example/api/piggy/",
    deployer.address
  );
  await piggy.waitForDeployment();
  const piggyAddr = await piggy.getAddress();
  console.log("PiggyNFT:", piggyAddr);

  // Demo airdrop 3 passes
  await (await piggy.mint(deployer.address)).wait();
  await (await piggy.mint(deployer.address)).wait();
  await (await piggy.mint(deployer.address)).wait();
  console.log("Done.");
}

main().catch((e) => { console.error(e); process.exit(1); });
