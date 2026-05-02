#!/usr/bin/env bash
set -euo pipefail

echo "Setting up AI-FACTORY-v2 advanced orchestrator..."

python -m venv venv
source venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt

mkdir -p gnap/requests gnap/results
if [ ! -f gnap/manifest.json ]; then
  cat > gnap/manifest.json << 'EOF'
{
  "version": "1.0",
  "protocol": "GNAP",
  "agents": [],
  "jobs": {},
  "created_at": "1970-01-01T00:00:00"
}
EOF
fi

if [ ! -f .env ]; then
  cat > .env << 'EOF'
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
GITHUB_TOKEN=your_token_here
EOF
fi

echo "Setup complete. Run: python main.py"
