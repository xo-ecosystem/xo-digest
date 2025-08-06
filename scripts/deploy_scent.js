const { ethers } = require("hardhat");

async function main() {
    console.log("👃 Deploying XO Scent Drop Contract...");
    
    // Get the contract factory
    const ScentDrop = await ethers.getContractFactory("ScentDrop");
    
    // Deploy the contract
    const scentDrop = await ScentDrop.deploy();
    await scentDrop.waitForDeployment();
    
    const address = await scentDrop.getAddress();
    console.log("✅ XO Scent Drop deployed to:", address);
    
    // Create initial scents
    console.log("🌸 Creating initial scents...");
    
    // Scent 1: Eternal Flame Scent
    const eternalFlameNotes = [
        "smoke",
        "amber",
        "vanilla"
    ];
    
    await scentDrop.createScent(
        "Eternal Flame Scent",
        "A warm, smoky fragrance inspired by the eternal flame of the XO universe",
        "ipfs://QmEternalFlameScent", // Replace with actual IPFS hash
        "https://xoseals.com/scents/eternal_flame",
        333, // Max supply
        ethers.parseEther("0.015"), // Price: 0.015 ETH
        eternalFlameNotes,
        "strong",
        "autumn"
    );
    
    console.log("✅ Created scent: Eternal Flame");
    
    // Scent 2: Cosmic Resonance Scent
    const cosmicResonanceNotes = [
        "ozone",
        "jasmine",
        "musk"
    ];
    
    await scentDrop.createScent(
        "Cosmic Resonance Scent",
        "An ethereal fragrance that captures the cosmic forces of the XO universe",
        "ipfs://QmCosmicResonanceScent", // Replace with actual IPFS hash
        "https://xo-vault.com/scents/cosmic_resonance",
        777, // Max supply
        ethers.parseEther("0.015"), // Price: 0.015 ETH
        cosmicResonanceNotes,
        "medium",
        "spring"
    );
    
    console.log("✅ Created scent: Cosmic Resonance");
    
    // Scent 3: Seal Breaker Scent
    const sealBreakerNotes = [
        "leather",
        "sage",
        "cedar"
    ];
    
    await scentDrop.createScent(
        "Seal Breaker Scent",
        "A mysterious fragrance that unlocks hidden knowledge and ancient wisdom",
        "ipfs://QmSealBreakerScent", // Replace with actual IPFS hash
        "https://xoseals.com/scents/seal_breaker",
        500, // Max supply
        ethers.parseEther("0.015"), // Price: 0.015 ETH
        sealBreakerNotes,
        "light",
        "winter"
    );
    
    console.log("✅ Created scent: Seal Breaker");
    
    // Add olfactory metadata
    console.log("📝 Adding olfactory metadata...");
    
    // Eternal Flame metadata
    await scentDrop.addOlfactoryNote(1, "smoke", JSON.stringify({
        "description": "Rich, warm smoke notes",
        "intensity": "strong",
        "duration": "long-lasting"
    }));
    
    await scentDrop.addOlfactoryNote(1, "amber", JSON.stringify({
        "description": "Deep, resinous amber",
        "intensity": "medium",
        "duration": "moderate"
    }));
    
    await scentDrop.addOlfactoryNote(1, "vanilla", JSON.stringify({
        "description": "Sweet, comforting vanilla",
        "intensity": "light",
        "duration": "short"
    }));
    
    // Cosmic Resonance metadata
    await scentDrop.addOlfactoryNote(2, "ozone", JSON.stringify({
        "description": "Fresh, electric ozone",
        "intensity": "strong",
        "duration": "short"
    }));
    
    await scentDrop.addOlfactoryNote(2, "jasmine", JSON.stringify({
        "description": "Floral, exotic jasmine",
        "intensity": "medium",
        "duration": "moderate"
    }));
    
    await scentDrop.addOlfactoryNote(2, "musk", JSON.stringify({
        "description": "Animalic, warm musk",
        "intensity": "light",
        "duration": "long-lasting"
    }));
    
    // Seal Breaker metadata
    await scentDrop.addOlfactoryNote(3, "leather", JSON.stringify({
        "description": "Rich, aged leather",
        "intensity": "medium",
        "duration": "moderate"
    }));
    
    await scentDrop.addOlfactoryNote(3, "sage", JSON.stringify({
        "description": "Herbal, cleansing sage",
        "intensity": "light",
        "duration": "short"
    }));
    
    await scentDrop.addOlfactoryNote(3, "cedar", JSON.stringify({
        "description": "Woody, grounding cedar",
        "intensity": "medium",
        "duration": "long-lasting"
    }));
    
    console.log("✅ Added olfactory metadata for all scents");
    
    // Save deployment info
    const deploymentInfo = {
        contractAddress: address,
        network: network.name,
        deployedAt: new Date().toISOString(),
        scents: {
            "eternal_flame": {
                scentId: 1,
                name: "Eternal Flame Scent",
                maxSupply: 333,
                price: "0.015 ETH",
                notes: eternalFlameNotes,
                intensity: "strong",
                season: "autumn"
            },
            "cosmic_resonance": {
                scentId: 2,
                name: "Cosmic Resonance Scent",
                maxSupply: 777,
                price: "0.015 ETH",
                notes: cosmicResonanceNotes,
                intensity: "medium",
                season: "spring"
            },
            "seal_breaker": {
                scentId: 3,
                name: "Seal Breaker Scent",
                maxSupply: 500,
                price: "0.015 ETH",
                notes: sealBreakerNotes,
                intensity: "light",
                season: "winter"
            }
        }
    };
    
    console.log("📋 Scent Deployment Summary:");
    console.log("Contract Address:", deploymentInfo.contractAddress);
    console.log("Network:", deploymentInfo.network);
    console.log("Scents Created:", Object.keys(deploymentInfo.scents).length);
    
    // Save to file
    const fs = require("fs");
    fs.writeFileSync(
        "scent-deployment-info.json",
        JSON.stringify(deploymentInfo, null, 2)
    );
    
    console.log("💾 Scent deployment info saved to scent-deployment-info.json");
    console.log("🎉 XO Scent Drop deployment complete!");
}

main()
    .then(() => process.exit(0))
    .catch((error) => {
        console.error("❌ Scent deployment failed:", error);
        process.exit(1);
    });
