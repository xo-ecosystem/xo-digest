const { ethers } = require("hardhat");

async function main() {
    console.log("🪙 Deploying XO 21NGO Token Contract...");

    // Get signers
    const [deployer] = await ethers.getSigners();
    console.log("Deploying with address:", deployer.address);

    // Generate treasury and liquidity wallet addresses
    // In production, these would be actual wallet addresses
    const treasuryWallet = "0x" + "1".repeat(40); // Placeholder - replace with actual address
    const liquidityWallet = "0x" + "2".repeat(40); // Placeholder - replace with actual address

    console.log("Treasury Wallet:", treasuryWallet);
    console.log("Liquidity Wallet:", liquidityWallet);

    // Get the contract factory
    const NGOToken = await ethers.getContractFactory("NGOToken");

    // Deploy the contract
    const ngoToken = await NGOToken.deploy(
        "XO 21NGO Token",
        "21NGO",
        21000000, // 21 million initial supply
        treasuryWallet,
        liquidityWallet
    );
    await ngoToken.waitForDeployment();

    const address = await ngoToken.getAddress();
    console.log("✅ XO 21NGO Token deployed to:", address);

    // Get contract info
    const contractInfo = await ngoToken.getContractInfo();
    console.log("📊 Contract Information:");
    console.log("- Total Supply:", ethers.formatEther(contractInfo.totalSupply_), "21NGO");
    console.log("- Sell Tax:", contractInfo.sellTaxPercentage_, "%");
    console.log("- Treasury Wallet:", contractInfo.treasuryWallet_);
    console.log("- Liquidity Wallet:", contractInfo.liquidityWallet_);
    console.log("- Trading Enabled:", contractInfo.tradingEnabled_);

    // Enable trading
    console.log("🔓 Enabling trading...");
    await ngoToken.setTradingEnabled(true);
    console.log("✅ Trading enabled");

    // Add some initial liquidity providers to tax exclusion
    console.log("📝 Setting up tax exclusions...");

    // Example: Add some addresses to tax exclusion (replace with actual addresses)
    const excludedAddresses = [
        "0x" + "3".repeat(40), // Example: DEX router
        "0x" + "4".repeat(40), // Example: Pair contract
        "0x" + "5".repeat(40)  // Example: Team wallet
    ];

    await ngoToken.batchSetTaxExclusion(excludedAddresses, true);
    console.log("✅ Tax exclusions set for", excludedAddresses.length, "addresses");

    // Mint some tokens to treasury for initial liquidity
    console.log("💰 Minting initial treasury allocation...");
    const treasuryAmount = ethers.parseEther("1000000"); // 1 million tokens
    await ngoToken.mint(treasuryWallet, treasuryAmount);
    console.log("✅ Minted", ethers.formatEther(treasuryAmount), "21NGO to treasury");

    // Mint some tokens to deployer for testing
    console.log("🧪 Minting test allocation...");
    const testAmount = ethers.parseEther("100000"); // 100k tokens
    await ngoToken.mint(deployer.address, testAmount);
    console.log("✅ Minted", ethers.formatEther(testAmount), "21NGO to deployer");

    // Save deployment info
    const deploymentInfo = {
        contractAddress: address,
        network: network.name,
        deployedAt: new Date().toISOString(),
        deployer: deployer.address,
        tokenInfo: {
            name: "XO 21NGO Token",
            symbol: "21NGO",
            totalSupply: ethers.formatEther(contractInfo.totalSupply_),
            sellTaxPercentage: Number(contractInfo.sellTaxPercentage_),
            treasuryWallet: contractInfo.treasuryWallet_,
            liquidityWallet: contractInfo.liquidityWallet_,
            tradingEnabled: contractInfo.tradingEnabled_
        },
        initialAllocations: {
            treasury: ethers.formatEther(treasuryAmount),
            deployer: ethers.formatEther(testAmount)
        },
        excludedAddresses: excludedAddresses
    };

    console.log("📋 21NGO Deployment Summary:");
    console.log("Contract Address:", deploymentInfo.contractAddress);
    console.log("Network:", deploymentInfo.network);
    console.log("Total Supply:", deploymentInfo.tokenInfo.totalSupply, "21NGO");
    console.log("Sell Tax:", deploymentInfo.tokenInfo.sellTaxPercentage, "%");

    // Save to file
    const fs = require("fs");
    fs.writeFileSync(
        "ngo-deployment-info.json",
        JSON.stringify(deploymentInfo, null, 2)
    );

    console.log("💾 21NGO deployment info saved to ngo-deployment-info.json");
    console.log("🎉 XO 21NGO Token deployment complete!");

    // Display next steps
    console.log("\n🚀 Next Steps:");
    console.log("1. Update treasury and liquidity wallet addresses");
    console.log("2. Add DEX router and pair addresses to tax exclusion");
    console.log("3. Provide initial liquidity on DEX");
    console.log("4. Enable trading for public");
    console.log("5. Set up governance contracts (optional)");
}

main()
    .then(() => process.exit(0))
    .catch((error) => {
        console.error("❌ 21NGO deployment failed:", error);
        process.exit(1);
    });
