# 🧪 ContextualDB - Complete Testing Guide

This guide will help you test the entire system to ensure everything works correctly after the cleanup.

## 🚀 Quick Test Overview

**3 Main Components to Test:**
1. **Backend API** - FastAPI server with processing pipeline  
2. **Database** - Supabase with vector search
3. **Chrome Extension** - Content capture and search UI

---

## 📋 Prerequisites

### Required Software
```bash
# Backend
- Python 3.12+
- uv (Python package manager)

# Database  
- Supabase account (free tier works)
- OpenAI API key (for embeddings)

# Frontend
- Chrome/Chromium browser
- Node.js 18+ (for building extension)
```

### Required Accounts
1. **Supabase**: [supabase.com](https://supabase.com) - Free tier sufficient
2. **OpenAI**: [platform.openai.com](https://platform.openai.com) - ~$0.10 for testing

---

## ⚙️ Setup Instructions

### 1. Database Setup (5 minutes)

1. **Create Supabase Project**
   ```bash
   # Go to https://supabase.com
   # Click "New Project"
   # Choose name: "contextualdb-test"
   ```

2. **Install Database Schema**
   ```sql
   -- Go to Supabase Dashboard > SQL Editor
   -- Copy/paste contents of db/schema.sql
   -- Click "RUN"
   ```

3. **Get API Keys**
   ```bash
   # Go to Settings > API
   # Copy these values:
   SUPABASE_URL=https://xyz.supabase.co
   SUPABASE_SERVICE_ROLE_KEY=eyJ0eXAi...
   ```

### 2. Backend Setup (3 minutes)

1. **Install Dependencies**
   ```bash
   cd backend
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   uv sync
   ```

2. **Create Environment File**
   ```bash
   # Create backend/.env
   cat > .env << EOF
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
   OPENAI_API_KEY=sk-your-openai-key
   EOF
   ```

3. **Start Backend Server**
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

### 3. Frontend Setup (2 minutes)

1. **Build Extension**
   ```bash
   cd frontend
   npm install
   npm run build
   ```

2. **Load in Chrome**
   ```bash
   # Open Chrome
   # Go to chrome://extensions/
   # Enable "Developer mode"
   # Click "Load unpacked"
   # Select frontend/dist folder
   ```

---

## 🧪 Testing Workflow

### Test 1: Backend Health Check ✅

**Verify backend is running:**
```bash
curl http://localhost:8000/health
# Expected: {"message": "DB connection successful!"}
```

**If it fails:**
- Check Supabase credentials in `.env`
- Verify database schema was installed
- Check server logs for errors

### Test 2: Processing Pipeline ✅

**Test HTML processing:**
```bash
cd backend
python scripts/test_ingestion_service.py
```

**Expected output:**
```
✅ Processing test file: Building_a_web_search_engine.html
📊 Processing completed successfully
📄 Generated 15 chunks, 1 metadata entry
🎯 Context ID: abc-123-def
```

**If it fails:**
- Check OpenAI API key is valid
- Verify test HTML files exist in `app/processing/test_end_to_end/input/`

### Test 3: API Endpoints ✅

**Test ingestion endpoint:**
```bash
# Create test HTML file
echo "<html><body><h1>Test Page</h1><p>This is test content for ingestion.</p></body></html>" > test.html

# Test upload (replace USER_ID with real UUID)
curl -X POST http://localhost:8000/ingest \
  -F "contenthtml=@test.html" \
  -F "user_id=550e8400-e29b-41d4-a716-446655440000" \
  -F "file_name=test.html"
```

**Expected response:**
```json
{
  "success": true,
  "context_id": "abc-123-def",
  "chunks_count": 2,
  "metadata_count": 1
}
```

**Test search endpoint:**
```bash
curl "http://localhost:8000/search?query=test+content&user_id=550e8400-e29b-41d4-a716-446655440000"
```

**Expected response:**
```json
{
  "results": [
    {
      "id": "abc-123-def",
      "relevance_score": 0.85,
      "content": "This is test content...",
      "raw_html": "<html>...</html>"
    }
  ]
}
```

### Test 4: Chrome Extension ✅

**Test content capture:**

1. **Navigate to any webpage** (e.g., https://example.com)

2. **Click extension icon** in Chrome toolbar
   - Should show "Saving..." popup
   - Should process and upload content
   - Should show "Content Saved Successfully!" popup

3. **Open extension search**
   - Click extension icon → search panel
   - Enter search query: "example"
   - Should return relevant results

**Test search functionality:**

1. **Open search panel**
   ```bash
   # Click extension icon
   # Search panel should open on the side
   ```

2. **Search your content**
   ```bash
   # Enter query: "test content"
   # Should see results with:
   # - Relevance score (%)
   # - Content snippet
   # - Copy context button
   # - View HTML button
   ```

### Test 5: End-to-End Workflow ✅

**Complete user journey:**

1. **Capture multiple pages**
   - Visit 3-5 different websites
   - Click extension icon on each
   - Verify "saved successfully" messages

2. **Search across content**
   - Open search panel
   - Try different queries:
     - Specific terms from captured pages
     - General concepts
     - Questions about the content

3. **Use results**
   - Click "Copy context" to get LLM-ready text
   - Click "View HTML" to see original content
   - Verify relevance scores make sense

---

## 🔧 Troubleshooting

### Common Issues & Solutions

**Backend won't start:**
```bash
# Check environment variables
cat backend/.env

# Check Python dependencies
cd backend && uv sync

# Check Supabase connection
python -c "from app.core.supabase_client import supabase; print(supabase.table('contexts').select('*').limit(1).execute())"
```

**Extension not working:**
```bash
# Check extension is loaded
# Chrome → Extensions → ContextDB should be enabled

# Check permissions
# Extension should have "activeTab" permission

# Check network requests
# F12 → Network tab → look for failed API calls
```

**Search returns no results:**
```bash
# Check data was ingested
curl "http://localhost:8000/search?query=test&user_id=YOUR_USER_ID"

# Check database has data
# Supabase Dashboard → Table Editor → contexts table
```

**Processing fails:**
```bash
# Check OpenAI API key
curl -H "Authorization: Bearer $OPENAI_API_KEY" \
  https://api.openai.com/v1/models

# Check processing logs
tail -f backend/logs/app.log
```

---

## 📊 Sample Test Data

**Use these test HTML files for consistent testing:**

```html
<!-- test-article.html -->
<!DOCTYPE html>
<html>
<head>
    <title>How to Build a Search Engine</title>
    <meta name="description" content="Learn how to build a modern search engine with vector embeddings">
</head>
<body>
    <h1>Building Modern Search Engines</h1>
    <p>Search engines today use vector embeddings and semantic similarity to understand user queries beyond keyword matching.</p>
    <p>Key components include text preprocessing, embedding generation, and similarity scoring.</p>
</body>
</html>
```

```html
<!-- test-tutorial.html -->
<!DOCTYPE html>
<html>
<head>
    <title>Vector Database Tutorial</title>
</head>
<body>
    <h1>Introduction to Vector Databases</h1>
    <p>Vector databases store high-dimensional embeddings and enable fast similarity search.</p>
    <p>Popular options include Pinecone, Weaviate, and Supabase with pgvector.</p>
</body>
</html>
```

**Test queries to try:**
- "search engine" (should match first article)
- "vector database" (should match second article)  
- "embeddings" (should match both)
- "how to build" (should match first with higher score)

---

## ✅ Success Criteria

**All tests pass when:**

1. ✅ **Backend starts** without errors and `/health` returns success
2. ✅ **HTML processing** completes and generates chunks/embeddings  
3. ✅ **API endpoints** accept uploads and return search results
4. ✅ **Chrome extension** captures pages and shows in search
5. ✅ **End-to-end flow** works: capture → process → search → results

**Performance benchmarks:**
- Page capture: < 5 seconds
- Search response: < 2 seconds  
- Extension load: < 1 second

---

## 🐛 Getting Help

**If tests fail:**

1. **Check logs** in browser console and backend terminal
2. **Verify environment** variables are set correctly
3. **Test step-by-step** - isolate which component is failing
4. **Check network** requests in browser DevTools

**Log locations:**
- Backend: Terminal where `uvicorn` is running
- Frontend: Chrome DevTools → Console
- Extension: Chrome → Extensions → ContextDB → Inspect views

This testing guide ensures your ContextualDB system is working correctly! 🎯