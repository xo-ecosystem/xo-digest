require("@nomicfoundation/hardhat-toolbox");
require("@nomicfoundation/hardhat-verify");
require("dotenv").config();

const {
  PRIVATE_KEY,
  POLYGON_RPC_URL,
  POLYGONSCAN_API_KEY,
  ARBITRUM_RPC_URL,
  ARBISCAN_API_KEY,
  OPTIMISM_RPC_URL,
  OPTIMISM_API_KEY,
  BASE_RPC_URL,
  BASESCAN_API_KEY,
  SEPOLIA_RPC_URL,
  ETHERSCAN_API_KEY,
  MUMBAI_RPC_URL
} = process.env;

/** @type import('hardhat/config').HardhatUserConfig */
module.exports = {
  solidity: {
    version: "0.8.21",
    settings: {
      optimizer: {
        enabled: true,
        runs: 200
      }
    }
  },
  networks: {
    // Local Development
    localhost: {
      url: "http://127.0.0.1:8545",
      chainId: 31337
    },
    
    // Mainnet Networks
    polygon: {
      url: POLYGON_RPC_URL || "https://polygon-rpc.com",
      accounts: PRIVATE_KEY ? [PRIVATE_KEY] : [],
      chainId: 137,
      gasPrice: 30000000000 // 30 gwei
    },
    arbitrum: {
      url: ARBITRUM_RPC_URL || "https://arb1.arbitrum.io/rpc",
      accounts: PRIVATE_KEY ? [PRIVATE_KEY] : [],
      chainId: 42161,
      gasPrice: 100000000 // 0.1 gwei
    },
    optimism: {
      url: OPTIMISM_RPC_URL || "https://mainnet.optimism.io",
      accounts: PRIVATE_KEY ? [PRIVATE_KEY] : [],
      chainId: 10,
      gasPrice: 1000000 // 0.001 gwei
    },
    base: {
      url: BASE_RPC_URL || "https://mainnet.base.org",
      accounts: PRIVATE_KEY ? [PRIVATE_KEY] : [],
      chainId: 8453,
      gasPrice: 1000000000 // 1 gwei
    },
    
    // Testnet Networks
    polygonMumbai: {
      url: MUMBAI_RPC_URL || "https://rpc-mumbai.maticvigil.com",
      accounts: PRIVATE_KEY ? [PRIVATE_KEY] : [],
      chainId: 80001
    },
    arbitrumGoerli: {
      url: "https://goerli-rollup.arbitrum.io/rpc",
      accounts: PRIVATE_KEY ? [PRIVATE_KEY] : [],
      chainId: 421613
    },
    optimismGoerli: {
      url: "https://goerli.optimism.io",
      accounts: PRIVATE_KEY ? [PRIVATE_KEY] : [],
      chainId: 420
    },
    baseGoerli: {
      url: "https://goerli.base.org",
      accounts: PRIVATE_KEY ? [PRIVATE_KEY] : [],
      chainId: 84531
    },
    sepolia: {
      url: SEPOLIA_RPC_URL || "https://rpc.sepolia.org",
      accounts: PRIVATE_KEY ? [PRIVATE_KEY] : [],
      chainId: 11155111
    }
  },
  etherscan: {
    apiKey: {
      // Mainnet APIs
      polygon: POLYGONSCAN_API_KEY,
      arbitrumOne: ARBISCAN_API_KEY,
      optimisticEthereum: OPTIMISM_API_KEY,
      base: BASESCAN_API_KEY,
      
      // Testnet APIs
      polygonMumbai: POLYGONSCAN_API_KEY,
      arbitrumGoerli: ARBISCAN_API_KEY,
      optimismGoerli: OPTIMISM_API_KEY,
      baseGoerli: BASESCAN_API_KEY,
      sepolia: ETHERSCAN_API_KEY
    }
  },
  gasReporter: {
    enabled: process.env.REPORT_GAS !== undefined,
    currency: "USD"
  }
};
