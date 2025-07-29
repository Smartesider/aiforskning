#!/bin/bash

echo "🔧 Starter oppsett av GitHub Copilot CLI..."

gh extension install github/gh-copilot || echo "✅ Copilot CLI allerede installert"

unset GITHUB_TOKEN

if ! gh auth status &>/dev/null; then
  echo "🔑 Logger inn med GitHub OAuth..."
  gh auth login --web -h github.com
fi

echo 'eval "$(gh copilot alias -- bash)"' >> ~/.bashrc
source ~/.bashrc

echo "✅ Copilot CLI-oppsett ferdig!"
