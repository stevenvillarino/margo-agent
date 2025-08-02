#!/bin/bash

# 🔧 Development Environment Setup
# Sets up comprehensive development environment with all tools

echo "🔧 Setting up comprehensive development environment..."

# Run local setup first
bash scripts/setup_local.sh

# Install development dependencies
echo "📚 Installing development dependencies..."
pip install pytest black flake8 mypy jupyter notebook

# Install VS Code extensions (if code command is available)
if command -v code &> /dev/null; then
    echo "🔧 Installing recommended VS Code extensions..."
    code --install-extension ms-python.python
    code --install-extension ms-python.flake8
    code --install-extension ms-python.black-formatter
    code --install-extension charliermarsh.ruff
fi

# Set up pre-commit hooks
echo "🔗 Setting up pre-commit hooks..."
pip install pre-commit
cat > .pre-commit-config.yaml << 'PRECOMMIT'
repos:
  - repo: https://github.com/psf/black
    rev: 23.7.0
    hooks:
      - id: black
  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
PRECOMMIT

pre-commit install

# Create development configuration
cat > .vscode/settings.json << 'VSCODE'
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.formatting.provider": "black",
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "files.associations": {
        "*.md": "markdown"
    }
}
VSCODE

echo "✅ Development environment setup complete!"
echo ""
echo "🛠️ Development tools installed:"
echo "• Black (code formatting)"
echo "• Flake8 (linting)"
echo "• MyPy (type checking)"
echo "• Pytest (testing)"
echo "• Pre-commit hooks"
echo "• Jupyter Notebook"
