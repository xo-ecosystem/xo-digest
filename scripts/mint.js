const { ethers } = require("hardhat");

async function main() {
    console.log("🎫 Testing XO Drop Minting...");
    
    // Load deployment info
    const fs = require("fs");
    const deploymentInfo = JSON.parse(fs.readFileSync("deployment-info.json", "utf8"));
    
    // Get the deployed contract
    const XOSeason1Drop = await ethers.getContractFactory("XOSeason1Drop");
    const xoDrop = XOSeason1Drop.attach(deploymentInfo.contractAddress);
    
    // Get signer
    const [signer] = await ethers.getSigners();
    console.log("Minting with address:", signer.address);
    
    // Test minting message_bottle_v3 (Drop ID: 1)
    console.log("🌌 Minting message_bottle_v3...");
    
    try {
        const dropInfo = await xoDrop.getDrop(1);
        console.log("Drop Info:");
        console.log("- Name:", dropInfo.name);
        console.log("- Price:", ethers.utils.formatEther(dropInfo.price), "ETH");
        console.log("- Current Supply:", dropInfo.currentSupply.toString());
        console.log("- Max Supply:", dropInfo.maxSupply.toString());
        
        // Mint the drop
        const mintTx = await xoDrop.mintDrop(1, {
            value: dropInfo.price
        });
        
        console.log("⏳ Waiting for mint transaction...");
        await mintTx.wait();
        
        console.log("✅ Successfully minted message_bottle_v3!");
        console.log("Transaction hash:", mintTx.hash);
        
        // Check balance
        const balance = await xoDrop.balanceOf(signer.address, 1);
        console.log("Balance of message_bottle_v3:", balance.toString());
        
    } catch (error) {
        console.error("❌ Minting failed:", error.message);
    }
    
    // Test minting seal_flame (Drop ID: 2)
    console.log("\n🔥 Minting seal_flame...");
    
    try {
        const dropInfo = await xoDrop.getDrop(2);
        console.log("Drop Info:");
        console.log("- Name:", dropInfo.name);
        console.log("- Price:", ethers.utils.formatEther(dropInfo.price), "ETH");
        console.log("- Current Supply:", dropInfo.currentSupply.toString());
        console.log("- Max Supply:", dropInfo.maxSupply.toString());
        
        // Mint the drop
        const mintTx = await xoDrop.mintDrop(2, {
            value: dropInfo.price
        });
        
        console.log("⏳ Waiting for mint transaction...");
        await mintTx.wait();
        
        console.log("✅ Successfully minted seal_flame!");
        console.log("Transaction hash:", mintTx.hash);
        
        // Check balance
        const balance = await xoDrop.balanceOf(signer.address, 2);
        console.log("Balance of seal_flame:", balance.toString());
        
    } catch (error) {
        console.error("❌ Minting failed:", error.message);
    }
    
    // Display all owned tokens
    console.log("\n📊 Token Holdings:");
    for (let dropId = 1; dropId <= 2; dropId++) {
        const balance = await xoDrop.balanceOf(signer.address, dropId);
        if (balance.gt(0)) {
            const dropInfo = await xoDrop.getDrop(dropId);
            console.log(`- ${dropInfo.name}: ${balance.toString()} tokens`);
        }
    }
    
    console.log("\n🎉 Minting test complete!");
}

main()
    .then(() => process.exit(0))
    .catch((error) => {
        console.error("❌ Minting test failed:", error);
        process.exit(1);
    });
