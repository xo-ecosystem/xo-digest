name: Release Drop Deploy

on:
  push:
    tags:
      - 'v*.*.*'

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Init Submodules (xo-drops)
        run: git submodule update --init --recursive

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install tox requests

      - name: Run tox tests
        run: tox -e py311

      - name: Check if tests passed
        if: ${{ failure() }}
        run: |
          echo "❌ Tests failed. Halting deployment."
          exit 1

      - name: Build Pulse Artifact
        run: |
          mkdir -p dist
          echo "# Pulse for $GITHUB_REF_NAME" > dist/pulse.md
          echo "Built at $(date)" >> dist/pulse.md

      - name: Sync Drop Metadata from xo-drops
        run: |
          echo "🔄 Syncing drop metadata..."
          mkdir -p dist/metadata
          rsync -av drops/xo-drops/metadata/ dist/metadata/
          echo "📦 Bundling .coin.yml files..."
          find dist/metadata -name "*.coin.yml" -exec cat {} + > dist/metadata/bundled_coins.yml
          echo "🏷️  Version tag: $GITHUB_REF_NAME" > dist/metadata/version_tag.txt

      - name: Auto-sign Drop Metadata in XO Vault
        run: |
          echo "🔏 Signing drop metadata with XO Vault..."
          curl -X POST https://xo-node.com/vault/sign-all \
            -H "Content-Type: application/json" \
            -d '{"tag": "${{ github.ref_name }}"}'

      - name: Upload Drop Metadata to Arweave/IPFS
        run: |
          echo "📤 Uploading drop metadata to Arweave..."
          ./scripts/upload_to_arweave.sh dist/metadata/bundled_coins.yml "$GITHUB_REF_NAME"

      - name: Upload Pulse Artifact
        uses: actions/upload-artifact@v3
        with:
          name: pulse-md
          path: dist/pulse.md

      - name: Trigger Pulse Webhook
        env:
          GITHUB_REF_NAME: ${{ github.ref_name }}
        run: |
          curl -X POST https://xo-node.com/pulse-webhook \
            -H "Content-Type: application/json" \
            -d '{"tag": "${{ github.ref_name }}"}'

      - name: Auto-publish to GitHub Pages or IPFS/Arweave
        run: |
          echo "Publishing tag $GITHUB_REF_NAME to Arweave/IPFS..."
          # Example placeholder command
          ./scripts/publish_to_arweave.sh "$GITHUB_REF_NAME"
