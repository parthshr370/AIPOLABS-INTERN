# Deep Memory Researcher: Final Implementation Plan

## Project Overview & Mission

### Core Goal
Build an intelligent memory research system that combines **ReWOO planning** with **ReAct adaptability** to conduct deep, systematic research through mem0 memory databases. The system uses a **7-step simplified approach** with minimal complexity and maximum effectiveness.

### Key Innovation: Iterative Adaptive Research
The system follows a simple 7-step flow:
1. **Metadata Ingestion**: Bulk analyze silo with cheap LLM → nested JSON
2. **Query Processing**: Combine query + metadata → detailed research breakdown
3. **ReWOO-ReAct Loop**: Plan → Search → Adapt → Repeat
4. **Data Accumulation**: Collect all search results in growing context
5. **Analysis**: Process raw data → structured insights
6. **Report Generation**: Create comprehensive final report

---

## Context & Foundation Technologies

### What is mem0?
**Location**: `/home/your_user_id/Downloads/Playground/deep_memory_researcher_mem0/mem0`

mem0 is a memory management system that stores and retrieves conversational memories using semantic search. Key capabilities:

**Core Functions** (found in `/mem0/mem0/memory/main.py`):
- `search(query, user_id, limit, filters, threshold)` - Semantic similarity search
- `get_all(user_id, filters, limit)` - Metadata-based bulk retrieval  
- Built-in embedding models for semantic understanding
- Metadata filtering for precise queries
- User session scoping (user_id, agent_id, run_id)

**Search Strategy Insights**:
- **Threshold 0.3-0.5**: Exploratory, broad discovery
- **Threshold 0.6-0.8**: Focused, high-relevance results
- **Threshold 0.8+**: Precise, exact-match searches
- **Filters**: Critical for medical/domain-specific research

### What is CAMEL AI?
**Location**: `/home/your_user_id/Downloads/Playground/deep_memory_researcher_mem0/camel`

CAMEL AI provides role-playing conversational agents with structured reasoning capabilities.

**Key Components**:
- `ChatAgent`: Main agent class for LLM interactions
- `BaseMessage`: Message formatting and role assignment
- `ModelFactory`: Creates various LLM models (Gemini, OpenAI, etc.)
- `RolePlaying`: Multi-agent conversations and interactions

**Integration Pattern** (Reference: `/simple_react_agent.py`):
```python
# Clean CAMEL agent initialization pattern
model = ModelFactory.create(
    model_platform=ModelPlatformType.GEMINI,
    model_type=ModelType.GEMINI_2_5_PRO,
    api_key=GEMINI_API_KEY,
    model_config_dict={"temperature": 0.2}
)
agent = ChatAgent(system_message=system_message, model=model)
response = agent.step(BaseMessage.make_user_message("User", user_input))
```

---

## Simplified System Architecture

### File Structure (6 Files Only)

```
deep_memory_researcher/
├── main.py                    # Entry point & CLI
├── config.py                  # Constants & API keys
├── prompts.txt               # All system prompts
├── cache/
│   └── metadata.json         # Cached silo analysis
│
├── metadata_ingester.py      # Step 1: Silo analysis
├── query_processor.py        # Step 2: Query breakdown
├── research_engine.py        # Steps 3,4,5: ReWOO-ReAct
├── analysis_engine.py        # Step 6: Data insights
├── report_generator.py       # Step 7: Final report
└── memory_interface.py       # Basic mem0 operations
```

### 7-Step Data Flow

```
1. Metadata Ingestion (async) → 2. Query Processing → 3-5. ReWOO-ReAct Loop → 
6. Analysis Engine → 7. Report Generation
```

### Component Responsibilities (Simplified)

#### **main.py** (Entry Point)
**Purpose**: CLI interface and coordination
**Key Functions**:
- `main()` - CLI interface for user interactions
- `process_query(query, user_id)` - Main research flow coordinator

**Integration Pattern**: Based on `/simple_react_agent.py` main function structure

#### **config.py** (Configuration)
**Purpose**: Constants and API key management
**Contents**:
```python
USER_ID = "doctor_memory"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")  
MEM0_API_KEY = os.getenv("MEM0_API_KEY")
CACHE_DIR = "./cache"
```

#### **prompts.txt** (System Prompts)
**Purpose**: All detailed prompts in one place
**Format**: `PROMPT_KEY|Detailed prompt content here...`
**Examples**:
- `METADATA_ANALYZER|Analyze this medical memory silo...`
- `QUERY_PROCESSOR|Break down this query with metadata...`
- `RESEARCH_PLANNER|Plan research strategy for...`
- `SYNTHESIS_AGENT|Create comprehensive report from...`

#### **metadata_ingester.py** (Step 1)
**Purpose**: One-time silo analysis using cheap LLM
**Key Functions**:
- `ingest_silo_metadata(user_id)` - GET_ALL → Gemini Flash 1M → nested JSON
- `cache_metadata(user_id, metadata)` - Save to cache/metadata.json

**Implementation**: Use Gemini 2.5 Flash (1M context) to analyze complete memory set, let LLM create structured JSON of patterns, concepts, and insights.

#### **query_processor.py** (Step 2)
**Purpose**: Combine query + metadata → detailed research breakdown
**Key Functions**:
- `process_query(query, metadata)` - Create detailed research plan with questions to answer

**Output Example**:
```json
{
  "research_questions": [
    "How many diabetic patients are in the database?",
    "What are their demographics?", 
    "What treatments are they receiving?"
  ],
  "search_strategy": "iterative_patient_discovery",
  "priority_chunks": ["patient_names", "diabetes_mentions", "treatment_details"]
}
```

#### **research_engine.py** (Steps 3,4,5)  
**Purpose**: ReWOO-ReAct loop with data accumulation
**Key Functions**:
- `rewoo_react_loop(research_plan)` - Main iterative research process
- `execute_search(query, threshold)` - Single mem0 search operation
- `accumulate_data(new_results, context)` - Add results to growing context

**Process**: Plan search → Execute → Adapt strategy → Accumulate data → Repeat until complete

#### **analysis_engine.py** (Step 6)
**Purpose**: Process accumulated raw data into structured insights
**Key Functions**:
- `analyze_raw_data(accumulated_data)` - Raw search results → JSON insights plan

**Output**: Structured analysis with patterns, statistics, and key findings ready for report generation

#### **report_generator.py** (Step 7)
**Purpose**: Create final comprehensive report
**Key Functions**:
- `generate_report(metadata, analysis, insights)` - Everything → final markdown + JSON report

**Output**: Mixed format report with markdown narrative and JSON data blocks

#### **memory_interface.py** (Basic Operations)
**Purpose**: Simple mem0 wrapper functions  
**Key Functions**:
- `search(query, threshold=0.4, limit=20)` - Basic mem0 search
- `get_all(user_id, limit=1000)` - Bulk memory retrieval
- `progressive_search(query)` - Search with fallback thresholds

---

## Implementation Strategy (Simplified)

### Core Principles
1. **Simple & Direct**: Each file does ONE thing well
2. **LLM-Heavy**: Let Gemini handle complex logic, use code for coordination
3. **Iterative**: Build understanding through repeated simple searches
4. **Cache Smart**: Never re-analyze the silo unnecessarily

### 7-Step Implementation Flow

#### **Step 1: Metadata Ingestion (Async Background)**
```python
# metadata_ingester.py flow
1. mem0.get_all(user_id="doctor_memory", limit=1000)
2. Feed entire result to Gemini Flash 1M context
3. LLM outputs structured JSON with:
   - Patient names list
   - Available medical concepts
   - Data patterns and relationships
   - Search strategy recommendations
4. Cache result in cache/metadata.json
```

#### **Step 2: Query Processing**
```python  
# query_processor.py flow
1. Load cached metadata
2. Combine user query + metadata context
3. LLM creates detailed research breakdown:
   - What questions need answering
   - What search terms to use
   - What order to search in
   - Expected iterative patterns
```

#### **Steps 3-5: ReWOO-ReAct Research Loop**
```python
# research_engine.py flow
class ResearchEngine:
    def rewoo_react_loop(plan):
        context = ""
        while not_complete:
            # REASON: What to search next?
            next_search = planner_agent.reason(plan, context)
            
            # ACT: Execute the search  
            results = memory_interface.search(next_search.query)
            
            # OBSERVE: What did we learn?
            insights = observer_agent.observe(results, context)
            
            # ACCUMULATE: Add to growing context
            context += f"Search: {next_search.query}\nResults: {results}\n"
            
            # UPDATE: Adapt plan based on findings
            plan = planner_agent.update_plan(plan, insights)
```

#### **Step 6: Analysis Engine** 
```python
# analysis_engine.py flow
def analyze_raw_data(accumulated_data):
    # Feed all search results to analysis agent
    analysis_prompt = f"""
    Raw research data: {accumulated_data}
    Create structured insights JSON with:
    - Statistics and counts  
    - Patterns identified
    - Key findings by category
    - Evidence links to source memories
    """
    return analyzer_agent.step(analysis_prompt)
```

#### **Step 7: Report Generation**
```python
# report_generator.py flow
def generate_report(metadata, analysis, insights):
    # Combine everything into final report
    return synthesizer_agent.create_mixed_format_report(
        metadata=metadata,
        analysis=analysis, 
        insights=insights
    )
```

### Iterative Search Example
**Query**: "Find all diabetic patients and their treatment outcomes"

**Search Sequence**:
1. "list all patient names" → Get universe of patients
2. "diabetes" → Find diabetes-related memories  
3. "Maria Garcia diabetes" → Specific patient details
4. "Maria Garcia treatment" → Treatment information
5. "Maria Garcia outcome" → Results/outcomes
6. Repeat steps 3-5 for each diabetic patient found

### Error Handling (Keep Simple)
- **Empty Results**: Lower threshold 0.4 → 0.3 → 0.2, then try broader terms
- **API Failures**: Simple retry with exponential backoff
- **LLM Errors**: Provide fallback responses and continue
- **Cache Issues**: Regenerate metadata if cache corrupted

---

## Code Patterns & Integration

### CAMEL Agent Setup (From `/simple_react_agent.py`)
```python
# Clean model initialization - use everywhere
model = ModelFactory.create(
    model_platform=ModelPlatformType.GEMINI,
    model_type=ModelType.GEMINI_2_5_PRO,  # or GEMINI_2_5_FLASH for cheap ops
    api_key=os.getenv("GEMINI_API_KEY"),
    model_config_dict={"temperature": 0.2}
)

# Agent creation pattern
system_message = BaseMessage.make_assistant_message(
    role_name="SpecificRole",
    content="Your system prompt here"  # Load from prompts.txt
)
agent = ChatAgent(system_message=system_message, model=model)
response = agent.step(BaseMessage.make_user_message("User", user_input))
```

### mem0 Interface Patterns
```python
# Basic search with fallback
def progressive_search(query, user_id="doctor_memory"):
    thresholds = [0.5, 0.4, 0.3, 0.2]
    for threshold in thresholds:
        results = mem0.search(
            query=query,
            user_id=user_id, 
            threshold=threshold,
            limit=20
        )
        if results:
            return results
    
    # Final fallback - broader search
    return mem0.get_all(user_id=user_id, limit=50)
```

### Prompt Loading Pattern
```python
# Simple prompt loading from prompts.txt
def load_prompt(key):
    with open('prompts.txt', 'r') as f:
        for line in f:
            if line.startswith(f"{key}|"):
                return line.split('|', 1)[1].strip()
    return f"You are a helpful {key.lower()} assistant."
```

### Error Handling Pattern
```python
# Keep it simple - based on existing agent patterns
try:
    result = some_operation()
    return result
except Exception as e:
    console.print(f"[red]Error in {operation_name}: {e}[/red]")
    return fallback_result or {}
```

---

## Implementation Phases (Simplified)

### Phase 1: Core Infrastructure (30 minutes)
1. **Set up file structure** - Create 6 files + config + prompts.txt
2. **Implement memory_interface.py** - Basic mem0 wrapper functions
3. **Create config.py** - API keys and constants  
4. **Write prompts.txt** - All system prompts in one place

### Phase 2: Metadata & Query Processing (45 minutes)  
5. **Implement metadata_ingester.py** - GET_ALL → Gemini Flash → JSON cache
6. **Create query_processor.py** - Query + metadata → research plan
7. **Test metadata ingestion** with existing medical data

### Phase 3: Research Engine (60 minutes)
8. **Build research_engine.py** - ReWOO-ReAct loop with data accumulation
9. **Test iterative search** with simple queries
10. **Verify plan adaptation** based on search results

### Phase 4: Analysis & Reporting (45 minutes)
11. **Implement analysis_engine.py** - Raw data → structured insights  
12. **Create report_generator.py** - Final markdown + JSON output
13. **Build main.py** - CLI interface and coordination

### Success Criteria (Keep Simple)

**Must Work**:
- Analyze silo metadata and cache it properly
- Break down complex queries into search sequences
- Execute iterative searches that build understanding
- Generate readable reports with evidence links

**Performance Targets**:
- Complete queries in 2-3 minutes maximum
- Handle 1000+ memories in metadata analysis
- Graceful degradation when searches return empty

**Quality Measures**:
- Reports include specific patient names and details
- Evidence clearly links back to source memories  
- System adapts search strategy based on findings

---

## File Implementation Checklist

### ✅ **Files to Create** (6 Core + 3 Support)

#### **Core Research Files** 
- [ ] **main.py** - CLI interface, coordinates all components  
- [ ] **metadata_ingester.py** - Step 1: Silo analysis with Gemini Flash
- [ ] **query_processor.py** - Step 2: Query + metadata → research plan  
- [ ] **research_engine.py** - Steps 3-5: ReWOO-ReAct loop + data accumulation
- [ ] **analysis_engine.py** - Step 6: Raw data → structured insights
- [ ] **report_generator.py** - Step 7: Final markdown + JSON report
- [ ] **memory_interface.py** - Basic mem0 wrapper functions

#### **Support Files**
- [ ] **config.py** - API keys, constants (USER_ID, CACHE_DIR)
- [ ] **prompts.txt** - All system prompts (METADATA_ANALYZER|..., QUERY_PROCESSOR|..., etc.)
- [ ] **cache/metadata.json** - Cached silo analysis (auto-generated)

### ✅ **Function Implementation Checklist**

#### **main.py** 
- [ ] `main()` - CLI interface based on simple_react_agent.py pattern
- [ ] `process_query(query, user_id)` - Main research coordinator

#### **metadata_ingester.py**
- [ ] `ingest_silo_metadata(user_id)` - GET_ALL → Gemini Flash 1M → JSON
- [ ] `cache_metadata(user_id, metadata)` - Save to cache/metadata.json
- [ ] `load_cached_metadata(user_id)` - Load from cache if exists

#### **query_processor.py** 
- [ ] `process_query(query, metadata)` - Create detailed research breakdown
- [ ] `load_prompt(key)` - Simple prompt loading from prompts.txt

#### **research_engine.py**
- [ ] `rewoo_react_loop(research_plan)` - Main iterative research process
- [ ] `execute_search(query, threshold)` - Single search with memory_interface  
- [ ] `accumulate_data(new_results, context)` - Add to growing research context

#### **analysis_engine.py**
- [ ] `analyze_raw_data(accumulated_data)` - Process all search results → insights JSON

#### **report_generator.py**
- [ ] `generate_report(metadata, analysis, insights)` - Create final mixed format output

#### **memory_interface.py** 
- [ ] `search(query, threshold, limit)` - Basic mem0 search wrapper
- [ ] `get_all(user_id, limit)` - Bulk memory retrieval  
- [ ] `progressive_search(query)` - Search with fallback thresholds [0.5, 0.4, 0.3, 0.2]

### ✅ **Integration Requirements**
- [ ] **CAMEL agents** - Use ModelFactory + ChatAgent pattern from simple_react_agent.py
- [ ] **mem0 client** - Direct MemoryClient() usage for all searches  
- [ ] **Rich console** - Use console.print for user feedback like existing agents
- [ ] **Error handling** - Simple try/except with fallback responses
- [ ] **Gemini Flash** - Use GEMINI_2_5_FLASH for metadata analysis (1M context)
- [ ] **Gemini Pro** - Use GEMINI_2_5_PRO for research agents (complex reasoning)

---

## Next Steps: Ready to Implement

**Total estimated time**: ~3 hours for complete working system

The simplified architecture focuses on the essential 7-step flow with minimal complexity. Each component has a clear single responsibility, and the system leverages LLM capabilities for complex reasoning while keeping the code structure clean and maintainable.

**Key differentiator**: Iterative search building - instead of trying complex queries, build understanding through repeated simple searches that progressively reveal deeper insights about the memory silo contents.