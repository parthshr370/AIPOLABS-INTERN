# Mem0 SDK Functions: `get_all()` and `search()`

## `get_all()` Function

**Basic signature:**
```python
get_all(version="v1", **kwargs) -> List[Dict[str, Any]]
```

### Parameters:
- **version**: `"v1"` or `"v2"` (API version)
- **user_id**: Filter by specific user
- **agent_id**: Filter by specific agent  
- **app_id**: Filter by specific app
- **run_id**: Filter by specific run
- **metadata**: Dict for metadata filtering (e.g. `{"category": "medical"}`)
- **limit**: Max number of results (default varies by version)
- **top_k**: Similar to limit
- **page**: Page number (v2 only, for pagination)
- **page_size**: Results per page (v2 only)
- **org_id**: Organization ID
- **project_id**: Project ID

## `search()` Function

**Basic signature:**
```python
search(query, version="v1", **kwargs) -> List[Dict[str, Any]]
```

### Parameters:
- **query**: Required search string
- **version**: `"v1"` or `"v2"` (API version)
- **user_id**: Filter by specific user
- **agent_id**: Filter by specific agent
- **app_id**: Filter by specific app
- **run_id**: Filter by specific run
- **metadata**: Dict for metadata filtering
- **limit**: Max results to return
- **top_k**: Number of top results
- **threshold**: Similarity threshold (0.0-1.0)
- **filters**: Additional filtering dict
- **org_id**: Organization ID
- **project_id**: Project ID

### Key Differences:
- **`get_all()`**: Returns all memories (with optional filtering)
- **`search()`**: Requires query string, uses semantic search with similarity scoring

---

## Available Filters

### `get_all()` Filters:

**Identity filters:**
- `user_id="doctor_memory"` - Filter by user ID
- `agent_id="medical_agent"` - Filter by agent ID
- `app_id="healthcare_app"` - Filter by application ID
- `run_id="session_123"` - Filter by run/session ID

**Metadata filters:**
```python
metadata={
    "summary_fact": True,
    "patient_id": "patient_123",
    "category": "medical",
    "session_type": "consultation"
}
```

**Pagination filters:**
- `limit=50` - Max results to return
- `top_k=100` - Alternative to limit
- `page=1` - Page number (v2 only)
- `page_size=25` - Results per page (v2 only)

### `search()` Filters:

**Same identity filters as `get_all()`:**
- `user_id`, `agent_id`, `app_id`, `run_id`

**Search-specific filters:**
- `threshold=0.7` - Similarity threshold (0.0-1.0)
- `limit=20` - Max results
- `top_k=10` - Number of top matches

**Metadata filters (same as `get_all()`):**
```python
metadata={
    "patient_name": "John Doe",
    "diagnosis": "diabetes",
    "medication": True
}
```

**Additional filters dict:**
```python
filters={
    "date_range": {"start": "2024-01-01", "end": "2024-12-31"},
    "priority": "high"
}
```

## Examples:

```python
# get_all with filters
client.get_all(
    user_id="doctor_memory",
    limit=100,
    metadata={"summary_fact": True, "patient_id": "123"}
)

# search with filters  
client.search(
    query="diabetes medication",
    user_id="doctor_memory",
    threshold=0.8,
    limit=20,
    metadata={"category": "medical"}
)
```