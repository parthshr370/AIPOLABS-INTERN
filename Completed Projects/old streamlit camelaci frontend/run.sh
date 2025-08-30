#!/bin/bash

# CAMEL-AI MCP Frontend Runner
echo "🐪 Starting CAMEL-AI MCP Frontend..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from template..."
    if [ -f env.example ]; then
        cp env.example .env
        echo "✅ Created .env file from template. Please edit it with your API keys."
        echo "📝 Edit .env file and run this script again."
        exit 1
    else
        echo "❌ env.example not found. Please create .env file manually."
        exit 1
    fi
fi

# Check if requirements are installed
echo "📦 Checking dependencies..."
python -c "import streamlit, camel" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "📥 Installing dependencies..."
    pip install -r requirements.txt
fi

# Start Streamlit app
echo "🚀 Launching Streamlit application..."
streamlit run streamlit_app.py --server.port 8501 --server.address localhost

echo "🏁 Application stopped." 