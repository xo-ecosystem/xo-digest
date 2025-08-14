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
  // await (await ethers.getSigner()).sendTransaction({ to: await sAETH.getAddress(), value: ethers.parseEther("0.1") });
  // await (await (await ethers.getContractAt("ShieldAether", await sAETH.getAddress())).deposit({ value: 0 })).wait().catch(()=>{});

  console.log("Done.");
}

main().catch((e) => { console.error(e); process.exit(1); });
