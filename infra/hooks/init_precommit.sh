#!/bin/bash
if ! grep -q 'xo-core-precommit-essentials' .pre-commit-config.yaml; then
    echo "🔁 Applying XO precommit essentials..."
    cat xo-precommit.shared.yaml >> .pre-commit-config.yaml
    pre-commit install
    echo "✅ Done."
else
    echo "✅ XO essentials already present."
fi