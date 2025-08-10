const { ethers } = require("hardhat");

async function main() {
    console.log("🚀 Deploying XO Season 1 Drop Contract...");

    // Get the contract factory
    const XOSeason1Drop = await ethers.getContractFactory("XOSeason1Drop");

    // Deploy the contract
    const xoDrop = await XOSeason1Drop.deploy();
    await xoDrop.waitForDeployment();

    const address = await xoDrop.getAddress();
    console.log("✅ XO Season 1 Drop deployed to:", address);

    // Create initial drops
    console.log("📦 Creating initial drops...");

    // Drop 1: message_bottle_v3 (Legendary Evolution)
    const messageBottleV3Traits = [
        "message_bottle_legendary",
        "cosmic_resonance_legendary"
    ];

    await xoDrop.createDrop(
        "Message Bottle V3 - Legendary Evolution",
        "Legendary ascension of the original message bottle - achieving ultimate form with transcendent powers",
        "ipfs://QmMessageBottleV3Image", // Replace with actual IPFS hash
        "https://xo-vault.com/drops/message_bottle_v3",
        777, // Max supply
        ethers.parseEther("0.021"), // Price: 0.021 ETH
        messageBottleV3Traits
    );

    console.log("✅ Created drop: message_bottle_v3");

    // Drop 2: seal_flame
    const sealFlameTraits = [
        "eternal_flame",
        "seal_breaker"
    ];

    await xoDrop.createDrop(
        "Seal Flame",
        "An eternal flame that never extinguishes, representing the unbreakable spirit with the power to break ancient seals",
        "ipfs://QmSealFlameImage", // Replace with actual IPFS hash
        "https://xoseals.com/drops/seal_flame",
        500, // Max supply
        ethers.parseEther("0.021"), // Price: 0.021 ETH
        sealFlameTraits
    );

    console.log("✅ Created drop: seal_flame");

    // Add trait metadata for message_bottle_v3
    await xoDrop.addTrait(1, "message_bottle_legendary", JSON.stringify({
        "description": "Legendary ascension of A mysterious bottle containing a scroll with ancient wisdom - achieving ultimate form",
        "rarity": "legendary",
        "game_effects": {
            "mario_kart": {
                "legendary_speed": 5.0,
                "legendary_shield": 60,
                "legendary_gravity": 5.0
            },
            "sims": {
                "legendary_inspiration": 10,
                "legendary_aura": 30,
                "legendary_creativity": 10
            },
            "minecraft": {
                "legendary_vision": 1000,
                "legendary_finder": 200,
                "legendary_mining": 3.0
            }
        }
    }));

    await xoDrop.addTrait(1, "cosmic_resonance_legendary", JSON.stringify({
        "description": "Legendary ascension of Enhanced connection to the cosmic forces - achieving ultimate form",
        "rarity": "legendary",
        "game_effects": {
            "mario_kart": {
                "legendary_speed": 5.0,
                "legendary_shield": 60,
                "legendary_gravity": 5.0
            },
            "sims": {
                "legendary_inspiration": 10,
                "legendary_aura": 30,
                "legendary_creativity": 10
            },
            "minecraft": {
                "legendary_vision": 1000,
                "legendary_finder": 200,
                "legendary_mining": 3.0
            }
        }
    }));

    // Add trait metadata for seal_flame
    await xoDrop.addTrait(2, "eternal_flame", JSON.stringify({
        "description": "An eternal flame that never extinguishes, representing the unbreakable spirit",
        "rarity": "legendary",
        "game_effects": {
            "mario_kart": {
                "flame_boost": 0.3,
                "eternal_shield": 45
            },
            "sims": {
                "flame_inspiration": 4,
                "eternal_aura": 20
            },
            "minecraft": {
                "flame_light": 1000,
                "eternal_mining": 2.0
            }
        }
    }));

    await xoDrop.addTrait(2, "seal_breaker", JSON.stringify({
        "description": "The power to break ancient seals and unlock hidden knowledge",
        "rarity": "epic",
        "game_effects": {
            "mario_kart": {
                "seal_break": 0.25,
                "unlock_speed": 0.2
            },
            "sims": {
                "seal_wisdom": 3,
                "unlock_creativity": 2
            },
            "minecraft": {
                "seal_vision": 500,
                "unlock_finder": 100
            }
        }
    }));

    console.log("✅ Added trait metadata for all drops");

    // Save deployment info
    const deploymentInfo = {
        contractAddress: address,
        network: network.name,
        deployedAt: new Date().toISOString(),
        drops: {
            "message_bottle_v3": {
                dropId: 1,
                name: "Message Bottle V3 - Legendary Evolution",
                maxSupply: 777,
                price: "0.021 ETH",
                traits: messageBottleV3Traits
            },
            "seal_flame": {
                dropId: 2,
                name: "Seal Flame",
                maxSupply: 500,
                price: "0.021 ETH",
                traits: sealFlameTraits
            }
        }
    };

    console.log("📋 Deployment Summary:");
    console.log("Contract Address:", deploymentInfo.contractAddress);
    console.log("Network:", deploymentInfo.network);
    console.log("Drops Created:", Object.keys(deploymentInfo.drops).length);

    // Save to file
    const fs = require("fs");
    fs.writeFileSync(
        "deployment-info.json",
        JSON.stringify(deploymentInfo, null, 2)
    );

    console.log("💾 Deployment info saved to deployment-info.json");
    console.log("🎉 XO Season 1 Drop deployment complete!");
}

main()
    .then(() => process.exit(0))
    .catch((error) => {
        console.error("❌ Deployment failed:", error);
        process.exit(1);
    });
