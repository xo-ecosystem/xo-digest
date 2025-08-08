## Agent on Fly.io (Dev)

This guide prepares the XO Agent API (`xo_agents.api:app`) for Fly.io. Do not commit secrets.

### fly.agent.toml

Create `fly.agent.toml` in repo root:

```toml
app = "xo-agent"
primary_region = "ams"

[build]
  builder = "paketobuildpacks/builder:base"

[env]
  XO_ENVIRONMENT = "production"
  PORT = "8080"

[[services]]
  protocol = "tcp"
  internal_port = 8080
  processes = ["app"]

  [[services.ports]]
    handlers = ["http"]
    port = 80

  [[services.ports]]
    handlers = ["tls", "http"]
    port = 443
```

### Deploy steps (manual)

```bash
flyctl apps create xo-agent || true
flyctl secrets set XO_AGENT_SECRET=REDACTED
flyctl deploy --config fly.agent.toml --app xo-agent
flyctl status --app xo-agent
flyctl logs --app xo-agent
```

Verify:

```bash
curl -sSf https://xo-agent.fly.dev/health
```

# 🚀 XO Core Multi-Chain Deployment Guide

## 🌟 Overview

This guide covers deploying the complete XO ecosystem across multiple blockchain networks:

- **Polygon** (Mainnet & Mumbai Testnet)
- **Arbitrum One** (Mainnet & Goerli Testnet)
- **Optimism** (Mainnet & Goerli Testnet)
- **Base** (Mainnet & Goerli Testnet)
- **Sepolia** (Ethereum Testnet)

## 📋 Prerequisites

### 1. Environment Setup

```bash
# Copy the multi-chain environment template
cp templates/env.multichain .env

# Install dependencies
npm install
```

### 2. Required API Keys

Get your API keys from:

- **PolygonScan**: https://polygonscan.com/apis
- **Arbiscan**: https://arbiscan.io/apis
- **Optimism**: https://optimistic.etherscan.io/apis
- **BaseScan**: https://basescan.org/apis
- **Etherscan**: https://etherscan.io/apis

### 3. Wallet Setup

- **Private Key**: Your deployment wallet private key
- **Testnet ETH**: For testnet deployments
- **Mainnet ETH**: For mainnet deployments

## 🔧 Configuration

### Environment Variables

Edit your `.env` file with your values:

```bash
# Required
PRIVATE_KEY=0x...

# Mainnet Networks
POLYGON_RPC_URL=https://polygon-rpc.com
POLYGONSCAN_API_KEY=your_key_here

ARBITRUM_RPC_URL=https://arb1.arbitrum.io/rpc
ARBISCAN_API_KEY=your_key_here

OPTIMISM_RPC_URL=https://mainnet.optimism.io
OPTIMISM_API_KEY=your_key_here

BASE_RPC_URL=https://mainnet.base.org
BASESCAN_API_KEY=your_key_here

# Testnet Networks
MUMBAI_RPC_URL=https://rpc-mumbai.maticvigil.com
SEPOLIA_RPC_URL=https://rpc.sepolia.org
ETHERSCAN_API_KEY=your_key_here
```

## 🚀 Deployment Commands

### Local Development

```bash
# Start local node
npm run node

# Deploy to localhost
npm run deploy:local

# Test minting
npm run mint:test
```

### Testnet Deployments

```bash
# Individual testnet deployments
npm run deploy:mumbai          # Polygon Mumbai
npm run deploy:arbitrum-goerli # Arbitrum Goerli
npm run deploy:optimism-goerli # Optimism Goerli
npm run deploy:base-goerli     # Base Goerli
npm run deploy:sepolia         # Sepolia

# Deploy to all testnets
npm run deploy:all-testnet
```

### Mainnet Deployments

```bash
# Individual mainnet deployments
npm run deploy:polygon   # Polygon
npm run deploy:arbitrum  # Arbitrum One
npm run deploy:optimism  # Optimism
npm run deploy:base      # Base

# Deploy to all mainnets
npm run deploy:all-mainnet
```

### Contract Verification

```bash
# Verify contracts on mainnet
npm run verify:polygon
npm run verify:arbitrum
npm run verify:optimism
npm run verify:base
```

## 📦 What Gets Deployed

### 1. XO Season 1 Drop (ERC-1155)

**Drops Created:**

- **First Flip Teaser** (ID: 1)

  - Price: 0.021 ETH
  - Supply: 777
  - Traits: Vault Immutability, Inbox Mastery, Digest Compiler, Trait Evolution, Lore Weaving

- **Brie Edition** (ID: 2)

  - Price: 0.042 ETH
  - Supply: 1 (1/1)
  - Traits: Brie Unicorn, Scroll Bearer, Sentimental Core, First Edition

- **Eighth Seal 3D** (ID: 3)
  - Price: 0.063 ETH
  - Supply: 333
  - Traits: Scrollbearer Puppet, Message Bottle Unicorn, Physical Manifestation, Printable Magic

### 2. Scent Drop (ERC-1155)

**Scents Created:**

- **Eternal Flame** (ID: 1)

  - Price: 0.021 ETH
  - Supply: 777
  - Intensity: Strong
  - Season: Eternal

- **Cosmic Resonance** (ID: 2)

  - Price: 0.042 ETH
  - Supply: 333
  - Intensity: Ethereal
  - Season: Cosmic

- **Seal Breaker** (ID: 3)
  - Price: 0.063 ETH
  - Supply: 111
  - Intensity: Legendary
  - Season: Ancient

### 3. NGO Token (ERC-20)

**Configuration:**

- Initial Supply: 1,000,000 tokens
- Trading: Enabled
- Tax Exclusions: Set for deployer and contract addresses
- Sell Tax: 5% (2% to treasury, 3% to liquidity)

## 📊 Network Information

| Network         | Chain ID | RPC URL                               | Explorer                             |
| --------------- | -------- | ------------------------------------- | ------------------------------------ |
| Polygon         | 137      | https://polygon-rpc.com               | https://polygonscan.com              |
| Arbitrum        | 42161    | https://arb1.arbitrum.io/rpc          | https://arbiscan.io                  |
| Optimism        | 10       | https://mainnet.optimism.io           | https://optimistic.etherscan.io      |
| Base            | 8453     | https://mainnet.base.org              | https://basescan.org                 |
| Polygon Mumbai  | 80001    | https://rpc-mumbai.maticvigil.com     | https://mumbai.polygonscan.com       |
| Arbitrum Goerli | 421613   | https://goerli-rollup.arbitrum.io/rpc | https://goerli.arbiscan.io           |
| Optimism Goerli | 420      | https://goerli.optimism.io            | https://goerli-optimism.etherscan.io |
| Base Goerli     | 84531    | https://goerli.base.org               | https://goerli.basescan.org          |
| Sepolia         | 11155111 | https://rpc.sepolia.org               | https://sepolia.etherscan.io         |

## 🔍 Post-Deployment

### 1. Verify Contracts

After deployment, verify your contracts on the respective block explorers:

```bash
# Example verification command
npx hardhat verify --network polygon DEPLOYED_CONTRACT_ADDRESS
```

### 2. Test Minting

Test the minting functionality:

```bash
# Test minting on localhost
npm run mint:test

# Or use the multi-chain mint script
npx hardhat run scripts/mint.js --network polygon
```

### 3. Check Deployment Info

Each deployment creates a JSON file with contract addresses and configuration:

```bash
# Example: deployment-polygon-1234567890.json
{
  "network": "polygon",
  "chainId": 137,
  "contracts": {
    "xoSeason1Drop": "0x...",
    "scentDrop": "0x...",
    "ngoToken": "0x..."
  }
}
```

## 🛡️ Security Considerations

### 1. Private Key Security

- Never commit your `.env` file to version control
- Use hardware wallets for mainnet deployments
- Consider using environment-specific key management

### 2. Gas Optimization

- Monitor gas prices before deployment
- Use appropriate gas limits for each network
- Consider using gas estimation tools

### 3. Contract Verification

- Always verify contracts after deployment
- Keep deployment records for audit trails
- Test thoroughly on testnets first

## 🎯 Recommended Deployment Order

### 1. Testnet First

```bash
# Start with testnets
npm run deploy:all-testnet

# Test functionality
npm run mint:test
```

### 2. Mainnet Deployment

```bash
# Deploy to mainnet networks
npm run deploy:all-mainnet

# Verify contracts
npm run verify:polygon
npm run verify:arbitrum
npm run verify:optimism
npm run verify:base
```

### 3. Post-Deployment

- Update frontend with new contract addresses
- Configure web3 providers for all networks
- Set up monitoring and analytics
- Announce to community

## 🚨 Troubleshooting

### Common Issues

1. **Insufficient Gas**

   - Check gas prices on the target network
   - Increase gas limit if needed

2. **RPC Connection Issues**

   - Verify RPC URLs are correct
   - Check network connectivity
   - Try alternative RPC providers

3. **Contract Verification Failures**
   - Ensure compiler settings match
   - Check constructor arguments
   - Verify network selection

### Support

For deployment issues:

1. Check the deployment logs
2. Verify environment configuration
3. Test on localhost first
4. Check network status

## 🌟 Success Checklist

- [ ] Environment configured with all API keys
- [ ] Testnet deployment successful
- [ ] Contract functionality tested
- [ ] Mainnet deployment completed
- [ ] Contracts verified on block explorers
- [ ] Frontend updated with new addresses
- [ ] Community announcement prepared

**Happy deploying! 🚀✨**
