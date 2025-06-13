#!/usr/bin/env bash
set -e
LOG_DIR="$HOME/XO-LOGS"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/xo-onboard.log"
exec > >(tee -a "$LOG_FILE") 2>&1
echo "--- XO Onboard Log Start ---"
date

export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
export PATH="$PYENV_ROOT/shims:$PATH"
export DIRECTION=envrc


echo "🚀 XO Onboarding Started..."

# Check required tools
MISSING_TOOLS=()

for tool in pyenv direnv tox; do
  if ! command -v $tool >/dev/null 2>&1; then
    MISSING_TOOLS+=($tool)
  fi
done

if [ ${#MISSING_TOOLS[@]} -ne 0 ]; then
  echo "⚠️ Installing missing tools: ${MISSING_TOOLS[*]}"
  for tool in "${MISSING_TOOLS[@]}"; do
    echo "📦 Installing $tool..."
    brew install $tool || {
      echo "❌ Failed to install $tool. Please install it manually."
      exit 1
    }
    echo "✅ Installed $tool - version: $($tool --version 2>/dev/null || echo 'unknown')"
  done
fi

# Ensure pyenv and pyenv-virtualenv are initialized
if command -v pyenv 1>/dev/null 2>&1; then
  # Check if pyenv-virtualenv is installed
  if ! pyenv commands | grep -q virtualenv; then
    echo "⚠️ pyenv-virtualenv not installed."
    echo "ℹ️ You can install it via: brew install pyenv-virtualenv"
    echo "🔁 Falling back to basic venv setup..."
    USE_BASIC_VENV=true
  else
    USE_BASIC_VENV=false
  fi

  echo "📦 Using pyenv"
  echo "🔢 pyenv version: $(pyenv --version || echo 'not installed')"
  export PYENV_ROOT="$HOME/.pyenv"
  export PATH="$PYENV_ROOT/bin:$PATH"
  eval "$(pyenv init --path)"
  if [ "$USE_BASIC_VENV" = false ]; then
    eval "$(pyenv virtualenv-init -)"
  fi

  TOOL_VERSIONS_FILE=".tool-versions"

  if [[ ! -f "$TOOL_VERSIONS_FILE" ]]; then
    echo "⚠️ .tool-versions not found, checking siblings for fallback..."
    for repo in ../xo-drops ../xo-utils ../xo-agents; do
      if [[ -f "$repo/.tool-versions" ]]; then
        cp "$repo/.tool-versions" "$TOOL_VERSIONS_FILE"
        echo "✅ Fallback .tool-versions copied from $repo"
        break
      fi
    done
  fi

  if [[ -f "$TOOL_VERSIONS_FILE" ]]; then
    VERSION=$(cut -d' ' -f2 "$TOOL_VERSIONS_FILE")
    pyenv install -s "$VERSION"
    pyenv local "$VERSION"

    # Sync .tool-versions to sibling repos
    for repo in xo-drops xo-utils xo-agents; do
      if [[ -d "../$repo" ]]; then
        cp "$TOOL_VERSIONS_FILE" "../$repo/.tool-versions"
        echo "🔄 Synced .tool-versions to ../$repo"
      fi
    done
  fi

  PYTHON_VERSION=3.11.9
  if [ "$USE_BASIC_VENV" = false ]; then
    pyenv install -s $PYTHON_VERSION
    pyenv virtualenv -f $PYTHON_VERSION xo-core-env
    pyenv local xo-core-env
  else
    pyenv install -s $PYTHON_VERSION
    export VENV_PATH=".venv"
    python -m venv $VENV_PATH
    echo "source $VENV_PATH/bin/activate" > .envrc
    source $VENV_PATH/bin/activate
    echo "✅ Activated fallback venv: $VENV_PATH"
  fi
else
  echo "⚠️ pyenv not found, skipping Python version setup."
fi

# Install base dev tools
pip install --upgrade pip
pip install -r requirements.txt
echo "📦 Installed from requirements.txt"
pip install mypy pytest pre-commit

# Set up pre-commit hooks
pre-commit install

if command -v direnv 1>/dev/null 2>&1 && [[ -f .tool-versions ]]; then
  echo "layout python $(pyenv which python)" > .envrc
  direnv allow
fi

echo "✅ XO Onboarding Complete!"
echo "--- XO Onboard Log End ---"

# Auto-link submodules if xo-drops exists
if [[ -d xo-drops ]]; then
  echo "🔗 Linking xo-drops submodule..."
  git submodule add -f ./xo-drops drops/xo-drops || echo "⚠️ Already linked or failed to add"
fi

# Brewfile support
if [[ -f Brewfile ]]; then
  echo "🍺 Installing via Brewfile..."
  brew bundle --no-upgrade || echo "⚠️ Brew bundle failed"
fi