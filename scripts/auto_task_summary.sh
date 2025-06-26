#!/bin/bash

OUTPUT_DIR="docs/task_summaries"
mkdir -p "$OUTPUT_DIR"

# Define namespaces to export
namespaces=("vault" "pulse" "xo" "drop" "collections" "ci")

timestamp=$(date +"%Y%m%d_%H%M%S")

for ns in "${namespaces[@]}"; do
    output_file="$OUTPUT_DIR/${ns}_$timestamp.md"
    xo-fab summary --to-md --namespace="$ns" --save-to="$output_file"
    if ! git diff --quiet "$output_file"; then
        git add "$output_file"
    fi
done

if git diff --cached --quiet; then
    echo "No changes to commit."
else
    git commit -m "🔄 Auto-update task summaries @ $timestamp"
fi
