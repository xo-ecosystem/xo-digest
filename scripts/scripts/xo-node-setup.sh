#!/bin/bash

# XO~Node Terminal Suite Installer
# For macOS or Debian-based systems
# Includes code-server, ttyd, ranger, wezterm (CLI), zsh, fzf, bat, tmux

echo "🌱 XO~Node Setup: Installing terminal tools and dev environment..."

# Update package list (Linux)
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
  sudo apt update
  sudo apt install -y git curl wget unzip tmux ranger fzf bat zsh build-essential
fi

# macOS Brew install
if [[ "$OSTYPE" == "darwin"* ]]; then
  echo "🔧 Using Homebrew on macOS..."
  brew update
  brew install git curl wget tmux ranger fzf bat zsh
fi

# Install code-server (VS Code in browser)
echo "💻 Installing code-server..."
curl -fsSL https://code-server.dev/install.sh | sh

# Install ttyd (web terminal)
echo "🖥️ Installing ttyd..."
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
  sudo apt install -y cmake libjson-c-dev libwebsockets-dev
  git clone https://github.com/tsl0922/ttyd.git
  cd ttyd && mkdir build && cd build
  cmake ..
  make && sudo make install
  cd ~
elif [[ "$OSTYPE" == "darwin"* ]]; then
  brew install ttyd
fi

# Optional: install WezTerm CLI if supported
if [[ "$OSTYPE" == "darwin"* ]]; then
  brew install --cask wezterm
fi

# Enable zsh as default
echo "🌀 Setting zsh as default shell..."
chsh -s $(which zsh)

echo "✅ XO~Node Terminal Environment is ready!"
echo "• Run 'code-server' to start browser-based VS Code"
echo "• Run 'ttyd tmux' to start web terminal (can serve over HTTP)"
