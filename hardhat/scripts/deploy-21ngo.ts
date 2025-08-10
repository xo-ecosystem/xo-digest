import { ethers } from "hardhat";
import * as fs from "fs";
import * as path from "path";

async function main() {
  console.log("🚀 Deploying 21NGO Token...");

  // Load configuration
  const configPath = path.join(__dirname, "../contracts/token_config.json");
  const config = JSON.parse(fs.readFileSync(configPath, "utf8"));

  // Get deployer account
  const [deployer] = await ethers.getSigners();
  console.log("📝 Deploying with account:", deployer.address);
  console.log("💰 Account balance:", (await deployer.getBalance()).toString());

  // Validate configuration
  if (config.deployment.treasuryAddress === "0x0000000000000000000000000000000000000000") {
    console.log("⚠️  Warning: Treasury address not set in config. Using deployer as treasury.");
    config.deployment.treasuryAddress = deployer.address;
  }

  if (config.deployment.ownerAddress === "0x0000000000000000000000000000000000000000") {
    console.log("⚠️  Warning: Owner address not set in config. Using deployer as owner.");
    config.deployment.ownerAddress = deployer.address;
  }

  // Get network info
  const network = await ethers.provider.getNetwork();
  console.log("🌐 Network:", network.name, "(Chain ID:", network.chainId, ")");

  // Deploy the token
  console.log("📦 Deploying Token21NGO contract...");
  const Token21NGO = await ethers.getContractFactory("Token21NGO");

  const token = await Token21NGO.deploy(
    config.name,
    config.symbol,
    config.initialSupply,
    config.deployment.ownerAddress,
    config.deployment.treasuryAddress,
    {
      gasLimit: config.deployment.gasLimit,
    }
  );

  console.log("⏳ Waiting for deployment...");
  await token.deployed();

  console.log("✅ Token21NGO deployed to:", token.address);

  // Verify deployment
  console.log("🔍 Verifying deployment...");
  const name = await token.name();
  const symbol = await token.symbol();
  const totalSupply = await token.totalSupply();
  const treasury = await token.treasuryAddress();
  const owner = await token.owner();

  console.log("📊 Token Details:");
  console.log("   Name:", name);
  console.log("   Symbol:", symbol);
  console.log("   Total Supply:", ethers.utils.formatEther(totalSupply));
  console.log("   Treasury Address:", treasury);
  console.log("   Owner Address:", owner);

  // Save deployment info
  const deploymentInfo = {
    network: network.name,
    chainId: network.chainId,
    contractAddress: token.address,
    deployer: deployer.address,
    deploymentTime: new Date().toISOString(),
    config: config,
    verification: {
      name: name,
      symbol: symbol,
      totalSupply: totalSupply.toString(),
      treasuryAddress: treasury,
      owner: owner,
    }
  };

  const deploymentPath = path.join(__dirname, "../deployments/21ngo-deployment.json");
  fs.mkdirSync(path.dirname(deploymentPath), { recursive: true });
  fs.writeFileSync(deploymentPath, JSON.stringify(deploymentInfo, null, 2));

  console.log("💾 Deployment info saved to:", deploymentPath);

  // Generate verification command
  const explorerUrl = config.networks[network.name]?.explorer || "https://etherscan.io";
  console.log("\n🔗 Verification Links:");
  console.log(`   Contract: ${explorerUrl}/address/${token.address}`);
  console.log(`   Owner: ${explorerUrl}/address/${owner}`);
  console.log(`   Treasury: ${explorerUrl}/address/${treasury}`);

  console.log("\n🎉 21NGO Token deployment complete!");
  console.log("   Next steps:");
  console.log("   1. Verify contract on explorer");
  console.log("   2. Add liquidity to DEX");
  console.log("   3. Update landing page with contract address");
  console.log("   4. Create Vault proposal for token launch");
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error("❌ Deployment failed:", error);
    process.exit(1);
  });
