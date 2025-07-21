# 🧪 XOSealsDrop Contract (ERC1155)

Smart contract for minting XO Seal collectibles on Base / testnets.

## 🔧 Setup

```bash
cp .env.example .env
# Fill in PRIVATE_KEY, NEXT_PUBLIC_RPC_BASE, etc.
```

## 🚀 Deploy

```bash
npx hardhat run scripts/deploy.ts --network base
```

## 📚 Contract

- `XOSealsDrop.sol`: ERC1155 contract with mint and setURI functions
- Constructor requires:
  - `string memory uri`: Base metadata URI (e.g. `ipfs://.../{id}.json`)
  - `address initialOwner`: Owner of the contract
