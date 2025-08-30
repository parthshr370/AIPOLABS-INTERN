# Backend API - Contextual Database

FastAPI backend for the Contextual Database Chrome Extension. Handles webpage content ingestion, vector embeddings, and semantic search.

##  Quick Start

### Prerequisites
- Python 3.12+
- Supabase account and project
- Chrome extension for content capture

### 1. Environment Setup
```bash
# Clone the repository
cd aci-contextualDB/backend

# Create virtual environment
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
uv sync
```

### 2. Environment Variables
Create a `.env` file in the backend directory:
```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key
```

### 3. Database Setup
1. Go to your Supabase dashboard
2. Navigate to **SQL Editor**
3. Copy and paste the contents of `../db/schema.sql`
4. Click **Run** to execute

### 4. Start the Server
```bash
# Development mode with auto-reload
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Production mode
uvicorn main:app --host 0.0.0.0 --port 8000
```

##  API Endpoints

### Health Check
```bash
GET /health
# Returns: {"message": "Hello, World!"}
```

### Content Ingestion
```bash
POST /api/v1/ingest
```

### Content Search
```bash
GET /api/v1/search?query=your search query
```

## Database Schema

The backend uses a single `contexts` table with vector embeddings:

- **Vector Support**: Uses pgvector extension for semantic search
- **Row Level Security**: Each user only sees their own content
- **Metadata Storage**: Flexible JSONB field for additional data