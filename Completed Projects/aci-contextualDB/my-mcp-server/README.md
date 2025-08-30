# MCP Server for Contextual Database Search

This MCP (Model Context Protocol) server provides tools for searching through embeddings stored in a Supabase database using pgvector for semantic similarity search.

## Features

- **Semantic Search**: Search through text chunks and metadata using vector similarity
- **pgvector Integration**: Leverages Supabase's pgvector extension for efficient similarity search
- **User Authentication**: Respects Row Level Security (RLS) policies for data privacy
- **Configurable Parameters**: Adjustable similarity thresholds and result counts
- **Rich Results**: Returns detailed similarity scores and context information

## Tools Available

### 1. `search_embeddings`
Full-featured embedding search with all parameters configurable.

**Parameters:**
- `query` (string): The search query to find similar embeddings
- `user_id` (UUID): User ID for authentication and data access
- `top_k` (number, 1-20): Number of top results to return (default: 5)
- `similarity_threshold` (number, 0-1): Minimum similarity score threshold (default: 0.3)

**Example:**
```json
{
  "query": "How to build a web application with Supabase?",
  "user_id": "6890cf8d-7699-4eb8-a06e-391209b89ade",
  "top_k": 3,
  "similarity_threshold": 0.4
}
```

### 2. `quick_search`
Simplified search with default parameters for quick queries.

**Parameters:**
- `query` (string): The search query to find similar embeddings
- `user_id` (UUID): User ID for authentication and data access

**Example:**
```json
{
  "query": "Machine learning and AI",
  "user_id": "6890cf8d-7699-4eb8-a06e-391209b89ade"
}
```

## Architecture

```
MCP Client → MCP Server → Backend API → Supabase (pgvector)
                ↓
            FastAPI Backend
                ↓
        SemanticRetrieval Class
                ↓
            pgvector Queries
```

## Setup

### 1. Backend Requirements
- FastAPI backend running on port 8000 (default)
- Supabase database with pgvector extension enabled
- Proper RLS policies configured
- `SemanticRetrieval` class from your backend

### 2. Environment Variables
Set these in your MCP server environment:
```bash
BACKEND_URL=http://localhost:8000  # Your FastAPI backend URL
```

### 3. Database Schema
Ensure your Supabase database has these tables:
- `contexts` - Main context information
- `context_chunks` - Text chunks with embeddings (vector type)
- `context_metadata` - Metadata with embeddings (vector type)

## Usage

### Starting the MCP Server
```bash
cd my-mcp-server
npm run dev  # Starts on localhost:8787
```

### Starting the Backend
```bash
cd backend
python main.py  # Starts on localhost:8000
```

### Testing
```bash
# Test the MCP server
node test-mcp.js

# Or test the backend directly
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How to use Supabase?",
    "user_id": "your-user-id",
    "top_k": 5,
    "similarity_threshold": 0.3
  }'
```

## How It Works

1. **Query Processing**: The MCP server receives a search query and parameters
2. **Backend Call**: Makes an HTTP request to your FastAPI backend
3. **Embedding Generation**: Backend generates embeddings for the query using your configured model
4. **Vector Search**: Uses pgvector to find similar embeddings in your database
5. **Result Ranking**: Combines chunk and metadata similarity scores for ranking
6. **Response Formatting**: Returns structured results with relevance scores and content previews

## Search Algorithm

The system uses a composite scoring approach:
- **70% weight** on best chunk similarity
- **20% weight** on metadata similarity (if available)
- **10% weight** on number of matching chunks (diversity bonus)

## Error Handling

- Network errors are caught and reported
- Backend API errors include status codes and messages
- Invalid parameters are validated using Zod schemas
- Graceful fallbacks for missing data

## Performance Considerations

- pgvector indexes are optimized for cosine similarity
- Results are limited to prevent overwhelming responses
- Embedding generation is cached when possible
- RLS policies ensure efficient user data filtering

## Security

- All database queries respect Row Level Security (RLS)
- User authentication is required for all searches
- No sensitive data is exposed in error messages
- Input validation prevents injection attacks

## Troubleshooting

### Common Issues

1. **Backend Connection Failed**
   - Check if FastAPI is running on the correct port
   - Verify `BACKEND_URL` environment variable

2. **Authentication Errors**
   - Ensure user_id is a valid UUID
   - Check RLS policies in Supabase

3. **No Results Returned**
   - Lower the similarity threshold
   - Verify embeddings exist in the database
   - Check if the user has access to the data

### Debug Mode
Enable logging in your backend to see detailed search operations:
```python
logging.basicConfig(level=logging.DEBUG)
```

## Future Enhancements

- [ ] Batch search capabilities
- [ ] Filtering by date ranges or content types
- [ ] Semantic clustering of results
- [ ] Real-time search updates
- [ ] Advanced ranking algorithms
- [ ] Search result caching

## Contributing

This MCP server is designed to work with your existing Supabase backend. To extend functionality:

1. Add new tools in the `init()` method
2. Create corresponding backend endpoints
3. Update the README with new tool documentation
4. Add appropriate tests

## License

See the main project LICENSE file for details. 
