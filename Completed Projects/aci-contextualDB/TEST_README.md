# 🧪 Quick Testing Instructions

After the codebase cleanup, use these **3 simple ways** to verify everything is working:

## 🚀 Option 1: Automated Setup & Test (Recommended)

```bash
# 1. Run setup script
./setup_env_example.sh

# 2. Add your API keys to backend/.env:
# SUPABASE_URL=https://your-project.supabase.co
# SUPABASE_SERVICE_ROLE_KEY=your-service-key  
# OPENAI_API_KEY=sk-your-openai-key

# 3. Start backend
cd backend
source .venv/bin/activate
uvicorn main:app --reload

# 4. Run comprehensive test (in another terminal)
python quick_test.py
```

## 🔧 Option 2: Quick API Test with curl

```bash
# 1. Start backend server
cd backend && uvicorn main:app --reload

# 2. Run curl-based tests (in another terminal)
./curl_test.sh
```

## 🌐 Option 3: Manual Chrome Extension Test

```bash
# 1. Build extension
cd frontend && npm install && npm run build

# 2. Load in Chrome
# • Open chrome://extensions/
# • Enable "Developer mode" 
# • Click "Load unpacked"
# • Select frontend/dist folder

# 3. Test manually
# • Visit any webpage
# • Click extension icon
# • Should save content successfully
# • Open search panel and search your content
```

## ✅ What Should Work

**After cleanup, these features should work perfectly:**

- ✅ **Backend API**: All endpoints responding correctly
- ✅ **Content Processing**: HTML cleaning, chunking, embedding generation  
- ✅ **Vector Search**: Semantic similarity search with pgvector
- ✅ **Chrome Extension**: Content capture and search interface
- ✅ **Database Operations**: CRUD operations with proper user isolation

## 📊 Expected Test Results

```
🏥 Backend Health: ✅ DB connection successful
📤 Content Ingestion: ✅ HTML processed, chunks created
🔍 Search Results: ✅ Relevant results with similarity scores  
🎯 Extension UI: ✅ Content saved and searchable
```

## 🆘 If Tests Fail

1. **Check Prerequisites**: Python 3.12+, Node.js 18+, uv installed
2. **Verify Environment**: API keys in `.env` file are correct
3. **Database Setup**: Supabase schema from `db/schema.sql` is installed
4. **Check Logs**: Look for errors in terminal and browser console

## 📚 Detailed Documentation

- **Complete Guide**: `TESTING_GUIDE.md` - Comprehensive testing instructions
- **API Documentation**: `docs/API.md` - All API endpoints
- **Pipeline Details**: `docs/PIPELINE.md` - How content processing works
- **Database Schema**: `docs/SCHEMA.md` - Database structure

---

**🎯 Goal**: Verify the cleanup didn't break anything and all core functionality works as expected!