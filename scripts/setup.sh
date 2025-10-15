#!/bin/bash
# Setup script for AI Voice Knowledge Assistant

set -e

echo "🚀 Setting up AI Voice Knowledge Assistant..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your API keys and credentials"
    exit 1
fi

# Create necessary directories
echo "📁 Creating data directories..."
mkdir -p data/knowledge_base
mkdir -p data/faiss_index
mkdir -p logs

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt
pip install -r frontend/requirements.txt

# Create __init__.py files if missing
find backend -type d -exec touch {}/__init__.py \; 2>/dev/null || true

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your API keys"
echo "2. Run 'docker-compose up' to start services"
echo "3. Access frontend at http://localhost:8501"
echo "4. Access API at http://localhost:8000"
