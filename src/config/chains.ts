// src/config/chains.ts
export const CHAINS = {
    base: {
      rpc: `https://api.metamask.io/v1?key=${process.env.MM_API_KEY_ID}`,
      id: 8453,
    },
    polygon: {
      rpc: `https://polygon-mainnet.infura.io/v3/${process.env.INFURA_PROJECT_ID}`,
      id: 137,
    },
  };