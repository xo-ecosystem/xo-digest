# Shield Aether Deployment Guide

## Prerequisites

1. **Base Sepolia Test ETH**: Get test ETH from [Base Sepolia Faucet](https://www.coinbase.com/faucets/base-ethereum-sepolia-faucet)
2. **Wallet Address**: `0x87E2a5E0443a6221Cf60Ae9b67007E4CAF738645`

## Quick Deploy

### 1. Get Test ETH
Visit the Base Sepolia faucet and send test ETH to your wallet address.

### 2. Deploy Contracts
```bash
cd contracts
export PRIVATE_KEY=7d8814110ff239c38b41b0ee1e8ce1c9511ea2dad7211fa546e3a2ed6572299f
export BASE_SEPOLIA_RPC_URL=https://sepolia.base.org
npx hardhat run scripts/00_deploy.ts --network baseSepolia
```

### 3. Update Environment Variables
Copy the deployed contract addresses to your `.env.local` file:
```bash
cp env.example .env.local
# Edit .env.local with the actual addresses from deployment
```

### 4. Run Demo
```bash
npm run dev
# Visit http://localhost:3000/shield-demo
# Visit http://localhost:3000/piggy
```

## Contract Addresses

After deployment, you'll see addresses like:
- ShieldVault: `0x...`
- ShieldAether: `0x...`
- SeasonalMemecoin: `0x...`
- MiniAMM: `0x...`
- PiggyNFT: `0x...`

## GitHub Webhook Setup

1. **Add Repository Secret**: `GH_WEBHOOK_SECRET` with a random string
2. **Configure Webhook**:
   - Payload URL: `https://your-domain.com/webhook/github`
   - Content type: `application/json`
   - Secret: Same as `GH_WEBHOOK_SECRET`
   - Events: Select `Push` and `Pull request`

## Demo Flow

1. **Deploy**: Contracts are deployed with initial liquidity
2. **Generate Fees**: Transfer tokens to generate 2% fees
3. **Convert Fees**: Convert accumulated fees to ETH via AMM
4. **Redeem**: Burn sAETH to receive pro-rata ETH from vault
5. **Piggy NFT**: View live vault stats in on-chain NFT

## Testing

```bash
# Run demo flow
cd contracts
npx hardhat run scripts/01_demo_flow.ts --network baseSepolia
```

## Production Considerations

- Add proper access controls and pausability
- Implement circuit breakers
- Add comprehensive testing
- Consider using WETH instead of native ETH
- Add keeper rewards for fee conversion
- Implement proper fee mechanisms
