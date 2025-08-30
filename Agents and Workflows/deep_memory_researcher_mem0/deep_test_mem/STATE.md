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



# Deep Test Memory - Current State Analysis







## 🔍 ISSUES IDENTIFIED

### 1. **MODULE IMPORT ERROR**
**Problem**: `ModuleNotFoundError: No module named 'mem0'`
- `deep_test_mem/` files cannot import `mem0` because it's in parent directory
- Python path doesn't include the mem0 module from `../mem0/`

### 2. **INCORRECT IMPORT STRUCTURE**  
**Problem**: Files trying to import `from mem0 import MemoryClient`
- Should import from local mem0 directory: `../mem0/mem0/client/main.py`
- Current imports assume mem0 is pip-installed

### 3. **ENVIRONMENT LOADING ORDER**
**Problem**: `load_dotenv()` called after using env vars
- `MEM0_API_KEY = os.getenv("MEM0_API_KEY")` happens before `load_dotenv()`
- Variables will be None

### 4. **CAMEL MODULE ACCESS**
**Problem**: Similar issue with camel imports
- CAMEL is in `../camel/` directory but not in Python path

## 📁 CURRENT FILE STRUCTURE

```
deep_memory_researcher_mem0/
├── .env                          # Environment variables
├── mem0/                         # Mem0 source code
│   └── mem0/
│       └── client/
│           └── main.py          # MemoryClient class
├── camel/                        # CAMEL framework  
└── deep_test_mem/               # Our test directory
    ├── main.py                  # ❌ BROKEN - import errors
    ├── metadata_ingestion.py    # ❌ BROKEN - import errors  
    ├── prompts.py               # ✅ WORKING
    ├── rewoo_research_planner.py # ❌ BROKEN - import errors
    └── simple_react_agent.py    # ❌ BROKEN - import errors
```

## 🚨 IMMEDIATE FIXES NEEDED

1. **Fix Python Path**: Add parent directories to sys.path
2. **Fix Import Statements**: Update to use local modules
3. **Fix Environment Loading**: Move load_dotenv() to top
4. **Test API Connectivity**: Verify .env has correct keys

## ✅ WORKING COMPONENTS

- `prompts.py` - Contains all prompts correctly
- Project structure is logical
- Code logic is sound once imports work

## 🎯 NEXT ACTIONS

1. Fix import issues in all files
2. Add path management to access local modules
3. Test basic functionality
4. Verify API connectivity

## 🔧 TECHNICAL DEBT

- No error handling for missing API keys
- Hard-coded paths and configurations  
- No logging system
- No unit tests

## 📊 COMPLETION STATUS

- **Architecture**: ✅ COMPLETE (well designed)
- **Implementation**: ❌ BROKEN (import issues)
- **Testing**: ❌ NOT STARTED
- **Documentation**: ⚠️ PARTIAL

## 🚀 RECOVERY PLAN

1. **Phase 1**: Fix imports and basic functionality
2. **Phase 2**: Test with real data
3. **Phase 3**: Add error handling and logging
4. **Phase 4**: Full integration testing