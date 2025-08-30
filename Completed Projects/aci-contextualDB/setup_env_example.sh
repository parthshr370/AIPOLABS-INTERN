#!/bin/bash

# ContextualDB Environment Setup Script
# This script helps set up the development environment

echo "🚀 ContextualDB Environment Setup"
echo "=================================="

# Check prerequisites
echo "📋 Checking prerequisites..."

# Check Python
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    echo "✅ Python $PYTHON_VERSION found"
else
    echo "❌ Python 3 not found. Please install Python 3.12+"
    exit 1
fi

# Check Node.js (for frontend)
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo "✅ Node.js $NODE_VERSION found"
else
    echo "❌ Node.js not found. Please install Node.js 18+"
    exit 1
fi

# Check uv (Python package manager)
if command -v uv &> /dev/null; then
    echo "✅ uv package manager found"
else
    echo "❌ uv not found. Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    source ~/.bashrc
fi

echo ""
echo "⚙️  Setting up backend..."

# Setup backend
cd backend

# Create virtual environment
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    uv venv
else
    echo "📦 Virtual environment already exists"
fi

# Install dependencies
echo "📥 Installing dependencies..."
uv sync

echo ""
echo "🌐 Setting up frontend..."

# Setup frontend
cd ../frontend

# Install npm dependencies
if [ ! -d "node_modules" ]; then
    echo "📦 Installing npm packages..."
    npm install
else
    echo "📦 npm packages already installed"
fi

# Build extension
echo "🔨 Building Chrome extension..."
npm run build

cd ..

echo ""
echo "✅ Environment setup complete!"
echo ""
echo "🔧 Next steps:"
echo "1. Create backend/.env file with your API keys:"
echo "   SUPABASE_URL=https://your-project.supabase.co"
echo "   SUPABASE_SERVICE_ROLE_KEY=your-service-key"
echo "   OPENAI_API_KEY=sk-your-openai-key"
echo ""
echo "2. Set up Supabase database:"
echo "   • Copy db/schema.sql to Supabase SQL Editor"
echo "   • Run the schema to create tables"
echo ""
echo "3. Start the backend server:"
echo "   cd backend"
echo "   source .venv/bin/activate"
echo "   uvicorn main:app --reload"
echo ""
echo "4. Load Chrome extension:"
echo "   • Open chrome://extensions/"
echo "   • Enable Developer mode"
echo "   • Click 'Load unpacked'"
echo "   • Select frontend/dist folder"
echo ""
echo "5. Run quick test:"
echo "   python quick_test.py"
echo ""
echo "📚 See TESTING_GUIDE.md for detailed testing instructions"