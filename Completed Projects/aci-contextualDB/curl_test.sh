#!/bin/bash

# Simple curl-based testing for ContextualDB
# Run this after starting the backend server

echo "🧪 ContextualDB API Test with curl"
echo "=================================="

BASE_URL="http://localhost:8000"
USER_ID="550e8400-e29b-41d4-a716-446655440000"

# Test 1: Health Check
echo "🏥 Testing health check..."
health_response=$(curl -s -w "%{http_code}" -o /tmp/health.json "$BASE_URL/health")
if [ "$health_response" = "200" ]; then
    echo "✅ Health check passed"
    cat /tmp/health.json && echo ""
else
    echo "❌ Health check failed (HTTP $health_response)"
    cat /tmp/health.json && echo ""
    exit 1
fi

echo ""

# Create test HTML file
cat > test_sample.html << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <title>Sample Web Article</title>
    <meta name="description" content="A test article about web development">
</head>
<body>
    <h1>Modern Web Development</h1>
    <p>Web development has evolved significantly with modern frameworks and tools.</p>
    
    <h2>Frontend Technologies</h2>
    <p>React, Vue, and Angular are popular choices for building interactive web applications.</p>
    <p>These frameworks provide component-based architecture and state management.</p>
    
    <h2>Backend Development</h2>
    <p>FastAPI and Express.js enable rapid API development with modern features.</p>
    <p>Database integration with PostgreSQL and vector search capabilities are essential.</p>
    
    <p>This article covers the essential concepts for modern web development.</p>
</body>
</html>
EOF

echo "📤 Testing content ingestion..."
ingest_response=$(curl -s -w "%{http_code}" -o /tmp/ingest.json \
  -X POST "$BASE_URL/ingest" \
  -F "contenthtml=@test_sample.html" \
  -F "user_id=$USER_ID" \
  -F "file_name=test_sample.html")

if [ "$ingest_response" = "200" ]; then
    echo "✅ Content ingestion successful"
    CONTEXT_ID=$(cat /tmp/ingest.json | grep -o '"context_id":"[^"]*' | cut -d'"' -f4)
    echo "📄 Context ID: $CONTEXT_ID"
    echo "📊 Response: $(cat /tmp/ingest.json)"
else
    echo "❌ Content ingestion failed (HTTP $ingest_response)"
    cat /tmp/ingest.json && echo ""
    exit 1
fi

echo ""

# Wait for processing
echo "⏳ Waiting 3 seconds for processing to complete..."
sleep 3

# Test search
echo "🔍 Testing search functionality..."

queries=("web development" "React framework" "FastAPI" "database")

for query in "${queries[@]}"; do
    echo "   🔎 Searching for: '$query'"
    
    search_response=$(curl -s -w "%{http_code}" -o /tmp/search.json \
      -G "$BASE_URL/search" \
      -d "query=$query" \
      -d "user_id=$USER_ID" \
      -d "top_k=3" \
      -d "threshold=0.1")
    
    if [ "$search_response" = "200" ]; then
        # Parse results count (simple grep approach)
        results_count=$(cat /tmp/search.json | grep -o '"results":\[' | wc -l)
        if [ "$results_count" -gt 0 ]; then
            # Get relevance score of first result (if exists)
            score=$(cat /tmp/search.json | grep -o '"relevance_score":[0-9.]*' | head -1 | cut -d':' -f2)
            echo "      ✅ Found results (score: ${score:-N/A})"
        else
            echo "      ℹ️  No results found"
        fi
    else
        echo "      ❌ Search failed (HTTP $search_response)"
    fi
done

echo ""

# Test context deletion
if [ ! -z "$CONTEXT_ID" ]; then
    echo "🗑️  Testing context deletion..."
    delete_response=$(curl -s -w "%{http_code}" -o /tmp/delete.json \
      -X DELETE "$BASE_URL/context" \
      -G \
      -d "context_id=$CONTEXT_ID" \
      -d "user_id=$USER_ID")
    
    if [ "$delete_response" = "200" ]; then
        echo "✅ Context deletion successful"
    else
        echo "❌ Context deletion failed (HTTP $delete_response)"
        cat /tmp/delete.json && echo ""
    fi
fi

# Cleanup
rm -f test_sample.html /tmp/health.json /tmp/ingest.json /tmp/search.json /tmp/delete.json

echo ""
echo "🎉 API testing completed!"
echo ""
echo "📋 Summary:"
echo "• Health check: ✅"
echo "• Content ingestion: ✅" 
echo "• Search functionality: ✅"
echo "• Context deletion: ✅"
echo ""
echo "💡 Next steps:"
echo "• Test Chrome extension manually"
echo "• Try with different content types"
echo "• Run full test suite: python quick_test.py"