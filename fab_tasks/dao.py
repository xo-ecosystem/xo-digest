from invoke import task, Collection
import os
import json
import subprocess
from pathlib import Path


@task
def deploy_token(c, network="sepolia", dry_run=False, verify=False):
    """
    Deploy the 21NGO token to the specified network.

    Args:
        network (str): Target network (sepolia, base, ethereum)
        dry_run (bool): Show what would be done without deploying
        verify (bool): Verify contract on explorer after deployment
    """
    print(f"🚀 Deploying 21NGO Token to {network}")

    if dry_run:
        print("🔍 DRY RUN - Would deploy token with current config")
        return

    # Change to hardhat directory
    hardhat_dir = Path("hardhat")
    if not hardhat_dir.exists():
        print("❌ Hardhat directory not found")
        return

    os.chdir(hardhat_dir)

    try:
        # Compile contracts
        print("📦 Compiling contracts...")
        subprocess.run(["npx", "hardhat", "compile"], check=True)

        # Deploy token
        print(f"🚀 Deploying to {network}...")
        cmd = ["npx", "hardhat", "run", "scripts/deploy-21ngo.ts", "--network", network]
        subprocess.run(cmd, check=True)

        # Verify if requested
        if verify:
            print("🔍 Verifying contract...")
            # This would require additional setup with etherscan API keys
            print("⚠️  Manual verification required - check deployment output for links")

        print("✅ Token deployment complete!")

    except subprocess.CalledProcessError as e:
        print(f"❌ Deployment failed: {e}")
    finally:
        # Return to original directory
        os.chdir("..")


@task
def init_token(c, treasury_address=None, owner_address=None):
    """
    Initialize token configuration with addresses.

    Args:
        treasury_address (str): Treasury wallet address
        owner_address (str): Owner wallet address
    """
    print("⚙️  Initializing 21NGO token configuration...")

    config_path = Path("hardhat/contracts/token_config.json")
    if not config_path.exists():
        print("❌ Token config not found")
        return

    # Load current config
    with open(config_path, 'r') as f:
        config = json.load(f)

    # Update addresses if provided
    if treasury_address:
        config["deployment"]["treasuryAddress"] = treasury_address
        print(f"📝 Treasury address set to: {treasury_address}")

    if owner_address:
        config["deployment"]["ownerAddress"] = owner_address
        print(f"📝 Owner address set to: {owner_address}")

    # Save updated config
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)

    print("✅ Token configuration updated!")


@task
def token_status(c):
    """
    Check the status of the 21NGO token deployment.
    """
    print("📊 21NGO Token Status")
    print("=" * 40)

    # Check if deployment file exists
    deployment_path = Path("hardhat/deployments/21ngo-deployment.json")
    if deployment_path.exists():
        with open(deployment_path, 'r') as f:
            deployment = json.load(f)

        print(f"🌐 Network: {deployment['network']} (Chain ID: {deployment['chainId']})")
        print(f"📦 Contract: {deployment['contractAddress']}")
        print(f"👤 Owner: {deployment['verification']['owner']}")
        print(f"💰 Treasury: {deployment['verification']['treasuryAddress']}")
        print(f"📅 Deployed: {deployment['deploymentTime']}")

        # Get explorer URL
        network = deployment['network']
        explorer_url = deployment['config']['networks'].get(network, {}).get('explorer', 'https://etherscan.io')
        print(f"🔗 Explorer: {explorer_url}/address/{deployment['contractAddress']}")

    else:
        print("❌ No deployment found")
        print("   Run: fab dao.deploy-token to deploy the token")


@task
def update_landing(c, contract_address=None):
    """
    Update the landing page with the deployed token contract address.

    Args:
        contract_address (str): Contract address to update (auto-detected if not provided)
    """
    print("🌐 Updating landing page with token info...")

    # Get contract address
    if not contract_address:
        deployment_path = Path("hardhat/deployments/21ngo-deployment.json")
        if deployment_path.exists():
            with open(deployment_path, 'r') as f:
                deployment = json.load(f)
            contract_address = deployment['contractAddress']
        else:
            print("❌ No deployment found and no address provided")
            return

    # Update landing page
    landing_path = Path("public/21xo/index.html")
    if not landing_path.exists():
        print("❌ Landing page not found")
        return

    with open(landing_path, 'r') as f:
        content = f.read()

    # Update Uniswap link with contract address
    # This is a simple replacement - in production you'd want more sophisticated templating
    network = "base"  # Default to Base network
    uniswap_url = f"https://app.uniswap.org/#/swap?outputCurrency={contract_address}&chain=base"

    # Simple replacement of the Uniswap link
    content = content.replace(
        'href="https://uniswap.org"',
        f'href="{uniswap_url}"'
    )

    with open(landing_path, 'w') as f:
        f.write(content)

    print(f"✅ Landing page updated with contract: {contract_address}")
    print(f"🔗 Uniswap link: {uniswap_url}")


@task
def create_vault_proposal(c):
    """
    Create a Vault proposal for the token launch.
    """
    print("📋 Creating Vault proposal for 21NGO token launch...")

    # Get deployment info
    deployment_path = Path("hardhat/deployments/21ngo-deployment.json")
    if not deployment_path.exists():
        print("❌ No deployment found - deploy token first")
        return

    with open(deployment_path, 'r') as f:
        deployment = json.load(f)

    # Create proposal directory
    proposal_dir = Path("vault/proposals/21ngo_launch")
    proposal_dir.mkdir(parents=True, exist_ok=True)

    # Create proposal content
    proposal_content = f"""# 21NGO Token Launch Proposal

## Overview
The 21NGO token has been successfully deployed to {deployment['network']} network.

## Contract Details
- **Contract Address**: {deployment['contractAddress']}
- **Network**: {deployment['network']} (Chain ID: {deployment['chainId']})
- **Token Name**: {deployment['verification']['name']}
- **Token Symbol**: {deployment['verification']['symbol']}
- **Total Supply**: {deployment['verification']['totalSupply']}
- **Treasury**: {deployment['verification']['treasuryAddress']}
- **Owner**: {deployment['verification']['owner']}

## Features
- 21% sell tax funds DAO treasury
- Anti-bot protection
- Max transaction limits
- Treasury address can be updated by owner

## Next Steps
1. Verify contract on explorer
2. Add initial liquidity to DEX
3. Launch marketing campaign
4. Begin DAO governance

## Deployment Info
- **Deployed**: {deployment['deploymentTime']}
- **Deployer**: {deployment['deployer']}

## Links
- [Contract on Explorer]({deployment['config']['networks'][deployment['network']]['explorer']}/address/{deployment['contractAddress']})
- [Uniswap Trading](https://app.uniswap.org/#/swap?outputCurrency={deployment['contractAddress']}&chain=base)
- [21XO Foundation](https://21xo.foundation)

---
*Proposal created automatically by fab dao.create-vault-proposal*
"""

    # Write proposal
    proposal_file = proposal_dir / "proposal.md"
    with open(proposal_file, 'w') as f:
        f.write(proposal_content)

    print(f"✅ Vault proposal created: {proposal_file}")
    print("📝 Review and sign the proposal to make it official")


# Create namespace
ns = Collection("dao")
ns.add_task(deploy_token, "deploy-token")
ns.add_task(init_token, "init-token")
ns.add_task(token_status, "token-status")
ns.add_task(update_landing, "update-landing")
ns.add_task(create_vault_proposal, "create-vault-proposal")
