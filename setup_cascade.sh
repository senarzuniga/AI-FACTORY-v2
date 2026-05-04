#!/usr/bin/env bash
set -euo pipefail

echo "========================================="
echo "Cascade Orchestrator Setup"
echo "One Trigger -> Cascade -> Self-Learning -> Controlled Deployment"
echo "========================================="

mkdir -p data/learning generated logs config

if [[ ! -d .venv ]]; then
  python3 -m venv .venv
fi

source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install numpy pytest pytest-cov

if [[ ! -f data/learning/learning_data.json ]]; then
cat > data/learning/learning_data.json << 'EOF'
{
  "successful_patterns": [],
  "failure_patterns": [],
  "performance_metrics": {},
  "workflow_optimizations": []
}
EOF
fi

if [[ ! -f config/linked_apps.json ]]; then
cat > config/linked_apps.json << 'EOF'
{
  "apps": [
    {
      "name": "adaptive-sales-engine",
      "deploy_command": "echo linked deploy hook placeholder"
    }
  ]
}
EOF
fi

echo ""
echo "Setup complete."
echo "Run example:"
echo "  source .venv/bin/activate"
echo "  python cascade_orchestrator.py \"improve code quality and resilience\""
