#!/bin/bash

echo "🚀 Setting up MCP Server for Contextual Database Search"
echo "========================================================"

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js first."
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed. Please install npm first."
    exit 1
fi

echo "✅ Node.js and npm are installed"

# Install dependencies
echo "📦 Installing dependencies..."
npm install

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "🔧 Creating .env file..."
    cp env.example .env
    echo "⚠️  Please edit .env file with your backend URL"
else
    echo "✅ .env file already exists"
fi

# Check if backend is running
echo "🔍 Checking if backend is accessible..."
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Backend is running and accessible"
else
    echo "⚠️  Backend is not accessible at http://localhost:8000"
    echo "   Make sure your FastAPI backend is running:"
    echo "   cd ../backend && python main.py"
fi

echo ""
echo "🎯 Setup complete! To start the MCP server:"
echo "   npm run dev"
echo ""
echo "📚 For more information, see README.md"
echo ""
echo "🧪 To test the server:"
echo "   node test-mcp.js"
