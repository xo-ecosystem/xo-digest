const { ethers } = require("hardhat");
const fs = require("fs");
const path = require("path");

async function main() {
  const network = await ethers.provider.getNetwork();
  const networkName = network.name === "unknown" ? "localhost" : network.name;
  
  console.log(`🚀 Deploying XO Contracts to ${networkName} (Chain ID: ${network.chainId})`);
  
  // Deploy XO Season 1 Drop
  console.log("\n📦 Deploying XO Season 1 Drop Contract...");
  const XOSeason1Drop = await ethers.getContractFactory("XOSeason1Drop");
  const xoDrop = await XOSeason1Drop.deploy();
  await xoDrop.waitForDeployment();
  const xoDropAddress = await xoDrop.getAddress();
  console.log("✅ XO Season 1 Drop deployed to:", xoDropAddress);
  
  // Deploy Scent Drop
  console.log("\n👃 Deploying XO Scent Drop Contract...");
  const ScentDrop = await ethers.getContractFactory("ScentDrop");
  const scentDrop = await ScentDrop.deploy();
  await scentDrop.waitForDeployment();
  const scentDropAddress = await scentDrop.getAddress();
  console.log("✅ XO Scent Drop deployed to:", scentDropAddress);
  
  // Deploy NGO Token
  console.log("\n🌍 Deploying XO NGO Token Contract...");
  const NGOToken = await ethers.getContractFactory("NGOToken");
  const ngoToken = await NGOToken.deploy();
  await ngoToken.waitForDeployment();
  const ngoTokenAddress = await ngoToken.getAddress();
  console.log("✅ XO NGO Token deployed to:", ngoTokenAddress);
  
  // Create drops in XO Season 1 Drop
  console.log("\n🎨 Creating drops in XO Season 1 Drop...");
  
  // Create first_flip_teaser drop
  const firstFlipTeaserTx = await xoDrop.createDrop(
    "First Flip Teaser",
    "Demonstrates the full power of the XO Vault system",
    ethers.parseEther("0.021"),
    777,
    true
  );
  await firstFlipTeaserTx.wait();
  console.log("✅ Created first_flip_teaser drop (ID: 1)");
  
  // Create brie_edition drop
  const brieEditionTx = await xoDrop.createDrop(
    "Brie's Scroll-Bearing Unicorn",
    "A special 1/1 scroll-bearing unicorn created specifically for Brie",
    ethers.parseEther("0.042"),
    1,
    true
  );
  await brieEditionTx.wait();
  console.log("✅ Created brie_edition drop (ID: 2)");
  
  // Create eighth_seal_3d drop
  const eighthSeal3dTx = await xoDrop.createDrop(
    "Eighth Seal 3D",
    "Physical + Digital hybrid through 3D printable characters",
    ethers.parseEther("0.063"),
    333,
    true
  );
  await eighthSeal3dTx.wait();
  console.log("✅ Created eighth_seal_3d drop (ID: 3)");
  
  // Add trait metadata for first_flip_teaser
  console.log("\n🧩 Adding trait metadata...");
  const traits1 = [
    { trait: "Vault Immutability", metadata: "Legendary trait for permanent records" },
    { trait: "Inbox Mastery", metadata: "Epic trait for cross-universe communication" },
    { trait: "Digest Compiler", metadata: "Rare trait for daily lore compilation" },
    { trait: "Trait Evolution", metadata: "Legendary trait for living evolution" },
    { trait: "Lore Weaving", metadata: "Epic trait for community storytelling" }
  ];
  
  for (const trait of traits1) {
    await xoDrop.addTrait(1, trait.trait, trait.metadata);
  }
  console.log("✅ Added traits for first_flip_teaser");
  
  // Add trait metadata for brie_edition
  const traits2 = [
    { trait: "Brie Unicorn", metadata: "Legendary 1/1 scroll-bearing unicorn" },
    { trait: "Scroll Bearer", metadata: "Epic trait for ancient wisdom carrier" },
    { trait: "Sentimental Core", metadata: "Legendary trait for emotional connection" },
    { trait: "First Edition", metadata: "Legendary trait for historical significance" }
  ];
  
  for (const trait of traits2) {
    await xoDrop.addTrait(2, trait.trait, trait.metadata);
  }
  console.log("✅ Added traits for brie_edition");
  
  // Add trait metadata for eighth_seal_3d
  const traits3 = [
    { trait: "Scrollbearer Puppet", metadata: "Legendary 3D printable character" },
    { trait: "Message Bottle Unicorn", metadata: "Epic easter egg character" },
    { trait: "Physical Manifestation", metadata: "Legendary digital to physical bridge" },
    { trait: "Printable Magic", metadata: "Epic cross-realm magic" }
  ];
  
  for (const trait of traits3) {
    await xoDrop.addTrait(3, trait.trait, trait.metadata);
  }
  console.log("✅ Added traits for eighth_seal_3d");
  
  // Create scents in Scent Drop
  console.log("\n🌸 Creating scents in Scent Drop...");
  
  const scents = [
    {
      name: "Eternal Flame",
      description: "The scent of an eternal flame that never extinguishes",
      price: ethers.parseEther("0.021"),
      supply: 777,
      intensity: "strong",
      season: "eternal"
    },
    {
      name: "Cosmic Resonance",
      description: "The scent of cosmic energy and universal harmony",
      price: ethers.parseEther("0.042"),
      supply: 333,
      intensity: "ethereal",
      season: "cosmic"
    },
    {
      name: "Seal Breaker",
      description: "The scent of ancient seals being broken",
      price: ethers.parseEther("0.063"),
      supply: 111,
      intensity: "legendary",
      season: "ancient"
    }
  ];
  
  for (let i = 0; i < scents.length; i++) {
    const scent = scents[i];
    const tx = await scentDrop.createScent(
      scent.name,
      scent.description,
      scent.price,
      scent.supply,
      scent.intensity,
      scent.season,
      true
    );
    await tx.wait();
    console.log(`✅ Created scent: ${scent.name} (ID: ${i + 1})`);
  }
  
  // Add olfactory notes for scents
  console.log("\n👃 Adding olfactory notes...");
  
  const olfactoryNotes = [
    // Eternal Flame
    { scentId: 1, note: "Smoke", metadata: "Rich, warm smoke with hints of cedar" },
    { scentId: 1, note: "Ash", metadata: "Fine, powdery ash with mineral notes" },
    { scentId: 1, note: "Heat", metadata: "Radiant warmth with spicy undertones" },
    
    // Cosmic Resonance
    { scentId: 2, note: "Stardust", metadata: "Sparkling, ethereal dust with ozone notes" },
    { scentId: 2, note: "Nebula", metadata: "Mysterious, swirling cosmic energy" },
    { scentId: 2, note: "Void", metadata: "Deep, infinite space with cold notes" },
    
    // Seal Breaker
    { scentId: 3, note: "Ancient", metadata: "Time-worn, mysterious ancient power" },
    { scentId: 3, note: "Breaking", metadata: "Sharp, decisive breaking energy" },
    { scentId: 3, note: "Freedom", metadata: "Liberating, expansive freedom scent" }
  ];
  
  for (const note of olfactoryNotes) {
    await scentDrop.addOlfactoryNote(note.scentId, note.note, note.metadata);
  }
  console.log("✅ Added olfactory notes for all scents");
  
  // Configure NGO Token
  console.log("\n🌍 Configuring NGO Token...");
  
  // Enable trading
  await ngoToken.setTradingEnabled(true);
  console.log("✅ Trading enabled");
  
  // Set tax exclusions for common addresses
  const [deployer] = await ethers.getSigners();
  const commonAddresses = [
    deployer.address,
    xoDropAddress,
    scentDropAddress,
    "0x0000000000000000000000000000000000000000" // Zero address
  ];
  
  await ngoToken.batchSetTaxExclusion(commonAddresses, true);
  console.log("✅ Tax exclusions set");
  
  // Mint initial supply
  const initialMint = ethers.parseEther("1000000"); // 1M tokens
  await ngoToken.mint(deployer.address, initialMint);
  console.log("✅ Initial supply minted");
  
  // Save deployment info
  const deploymentInfo = {
    network: networkName,
    chainId: network.chainId,
    deployedAt: new Date().toISOString(),
    contracts: {
      xoSeason1Drop: {
        address: xoDropAddress,
        drops: {
          first_flip_teaser: { id: 1, name: "First Flip Teaser", price: "0.021 ETH", supply: 777 },
          brie_edition: { id: 2, name: "Brie's Scroll-Bearing Unicorn", price: "0.042 ETH", supply: 1 },
          eighth_seal_3d: { id: 3, name: "Eighth Seal 3D", price: "0.063 ETH", supply: 333 }
        }
      },
      scentDrop: {
        address: scentDropAddress,
        scents: {
          eternal_flame: { id: 1, name: "Eternal Flame", price: "0.021 ETH", supply: 777 },
          cosmic_resonance: { id: 2, name: "Cosmic Resonance", price: "0.042 ETH", supply: 333 },
          seal_breaker: { id: 3, name: "Seal Breaker", price: "0.063 ETH", supply: 111 }
        }
      },
      ngoToken: {
        address: ngoTokenAddress,
        initialSupply: "1,000,000",
        tradingEnabled: true
      }
    },
    deployer: deployer.address
  };
  
  const filename = `deployment-${networkName}-${Date.now()}.json`;
  fs.writeFileSync(filename, JSON.stringify(deploymentInfo, null, 2));
  console.log(`\n💾 Deployment info saved to ${filename}`);
  
  console.log("\n🎉 Multi-chain deployment completed successfully!");
  console.log(`\n📊 Summary for ${networkName}:`);
  console.log(`- XO Season 1 Drop: ${xoDropAddress}`);
  console.log(`- Scent Drop: ${scentDropAddress}`);
  console.log(`- NGO Token: ${ngoTokenAddress}`);
  console.log(`- Deployer: ${deployer.address}`);
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error("❌ Multi-chain deployment failed:", error);
    process.exit(1);
  });
