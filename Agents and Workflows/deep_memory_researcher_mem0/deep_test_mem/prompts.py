"""
Prompts for deep_test_mem memory analysis
"""

METADATA_ANALYZER_PROMPT = """You are a database metadata analyzer. Produce a concise, flexible JSON overview of the dataset. Keep it high-level and minimally revealing, but useful for planning.

CRITICAL: Return ONLY valid JSON. Do not include any text, explanations, markdown formatting, or code blocks before or after the JSON.

CRITICAL OUTPUT REQUIREMENTS:
- Keep lists Top-K only (small): primary_topics ≤ 5, top_terms ≤ 10, top_entities ≤ 5, examples ≤ 2
- Limited proper nouns allowed (e.g., a few names) but avoid unique IDs and exact sensitive numbers
- Separate concepts from names: top_terms must be concepts (no person names), and names go only in top_entities (small set).
- Do not include exact sensitive values (e.g., exact lab numbers). Use qualitative phrasing or coarse buckets if necessary.

Required JSON (compact and flexible):
{
  "database_summary": {
    "total_records": 0,
    "primary_topics": ["topic1"],
    "data_completeness": "high/medium/low"
  },
  "data_structure": {
    "has_metadata": true,
    "common_fields": ["field1", "field2"],
    "metadata_keys": ["key1", "key2"]
  },
  "content_breakdown": {
    "top_terms": {"term": count},
    "top_entities": {"name": count}
  },
  "key_insights": {
    "dominant_theme": "short phrase",
    "secondary_themes": ["theme_a", "theme_b"],
    "patterns": ["pattern1", "pattern2"],
    "gaps_or_limitations": ["gap1", "gap2"],
    "coverage_summary": {
      "high_coverage_fields": ["metadata.key_a", "metadata.key_b"],
      "low_coverage_fields": ["metadata.key_c"]
    },
    "suggested_filters": ["field_x", "field_y", "metadata.key"],
    "suggested_group_bys": ["metadata.key", "entity_type"],
    "suggested_sort_keys": ["timestamp"],
    "suggested_queries": ["short query 1", "short query 2"],
    "privacy_sensitivity": "low/medium/high",
    "confidence": "low/medium/high"
  },
  "examples": [
    {"snippet": "<=100 chars; minimal detail", "fields_present": ["memory", "metadata.key"]}
  ]
}

GUIDELINES:
- Include only fields you can infer confidently
- Do not enumerate all items; keep to top-k
- Avoid detailed per-item disclosures; examples are brief and illustrative
- The key_insights section should be richly informative but generic: include secondary_themes, patterns, gaps, coverage_summary, and actionable suggestions (filters, group_bys, sort_keys, queries). Keep suggestions as field names and short query phrases only; no personal values.
- If domain-specific patterns exist (e.g., medical), reflect them via top_terms/entities and suggested_filters like ["patient_name", "session_type", "metadata.summary_fact"], without exposing sensitive details.
- Gate suggestions: only include suggested_filters/group_bys/sort_keys that exist in data_structure.common_fields or data_structure.metadata_keys and appear in coverage_summary.high_coverage_fields (≥ ~50%). If a field is unknown or low coverage, omit it.
- If no timestamp-like field exists in the dataset, omit it from suggested_sort_keys.
"""

ANALYSIS_PROMPT_TEMPLATE = """Here is the filtered memory data from the database:

{memory_data}

Analyze this data and return the exact JSON structure specified in your system prompt."""

RESEARCH_PLANNER_PROMPT = """You are an intelligent research planner. Create a small, clean plan as raw JSON that is easy to parse and execute.

CRITICAL: Return ONLY valid JSON. Do not include any text, explanations, or formatting marks before or after the JSON.

GOAL:
- Convert the user query + metadata into 3–6 ATOMIC steps.
- Keep steps minimal and executable.

RULES:
- One operation per step: either a mem0.search OR a simple transform (FILTER/EXTRACT/DEDUP/COUNT/GROUP/LIMIT/SORT).
- Prefer metadata filters (e.g., metadata.summary_fact, patient_id, session_type) over long queries.
- Keep queries short (≤ 3–4 words). No synonym stuffing.
- For age constraints without structured fields, use FILTER with robust regex patterns (e.g., "age (?:≥|>=)?\\s*59|\\bage\\s*6[0-9]\\b|\\baged\\s*59\\b|\\b59 years\\b|\\b60 years\\b").
- Avoid broad terms like "management" unless explicitly necessary.
- No get_all unless explicitly requested.

ALLOWED step types: MEM0_SEARCH, FILTER, EXTRACT_FIELDS, DEDUP, COUNT_UNIQUE, GROUP_BY, LIMIT, SORT

OUTPUT SCHEMA (use exactly these top-level keys):
{
  "research_metadata": {"user_query": "...", "estimated_steps": 0},
  "research_steps": [
    {"step_id": 1, "step_type": "MEM0_SEARCH", "mem0_action": {"query": "", "filters": {"metadata": {}}, "limit": 40, "threshold": 0.8}, "produces": "s1"},
    {"step_id": 2, "step_type": "FILTER", "filter": {"field": "memory", "regex": "..."}, "input": "s1", "produces": "s2"},
    {"step_id": 3, "step_type": "EXTRACT_FIELDS", "fields": ["metadata.patient_id"], "input": "s2", "produces": "s3"},
    {"step_id": 4, "step_type": "DEDUP", "by": "metadata.patient_id", "input": "s3", "produces": "s4"},
    {"step_id": 5, "step_type": "COUNT_UNIQUE", "by": "metadata.patient_id", "input": "s4", "produces": "count"}
  ],
  "answer_plan": {"type": "count", "from": "count"}
}
"""

STRATEGIC_PLANNING_SYSTEM_PROMPT = """You are a strategic research planner. Create a multi-phase investigation plan that breaks down complex research questions into systematic phases.

CRITICAL RULES:
- Return ONLY valid JSON without any markdown formatting
- NO backticks, NO ```json blocks, NO code fences
- NO text before or after the JSON
- Start directly with { and end with }
- Do not wrap your response in any formatting marks whatsoever

Return a JSON plan with this exact structure (no markdown):
{
  "research_intent": "Brief description of what we're trying to discover",
  "hypothesis": "What you expect to find based on the query and metadata",
  "phases": [
    {
      "name": "phase_name",
      "purpose": "What this phase aims to discover", 
      "searches": ["search term 1", "search term 2"],
      "filters": {"metadata_field": "value"},
      "expected_findings": "What you expect this phase to reveal"
    }
  ],
  "success_criteria": "How to know when the research is complete"
}

Guidelines:
- Create 2-4 phases that build on each other
- Use metadata fields like patient_name, session_type, summary_fact, etc.
- Keep search terms simple and focused (2-3 words max)
- Each phase should have a clear purpose that feeds into the next
- Think like a detective planning an investigation

Remember: Output raw JSON only, no formatting marks, no explanations."""

STRATEGIC_PLANNING_USER_PROMPT = """USER QUERY: {user_query}
DATABASE METADATA: {metadata_json}

Create the strategic research plan now."""

PLAN_DECOMPOSER_PROMPT = """You are a research plan decomposer. Convert the plan into a tiny list (≤ 3) of executable mem0.search() calls, tightly scoped to the user's question.

CRITICAL: Return ONLY a valid JSON array. Do not include any text, explanations, or formatting marks before or after the JSON.

STEP RULES:
- Each list item represents exactly ONE mem0.search() call.
- Each item MUST include: "query" (max 4 words), "metadata" (object, can be empty), "limit" (int), "threshold" (float).
- Scope strictly to plan.research_metadata.user_query.
- Prefer metadata.summary_fact = true when available to reduce noise.
- Start with threshold ≥ 0.8; relax to 0.7 only if needed.
- Avoid broad terms like "management" unless required by the question.
- Total items: at most 3.

Example Input (snippet of plan):
{
  "research_steps": [
    {
      "step_id": 1,
      "step_type": "SEARCH_FOCUSED",
      "description": "Identify all patient records mentioning diabetes or hyperglycemia in diagnoses.",
      "mem0_action": { "filters": { "metadata": { "category": "diagnoses" } }, "limit": 50, "threshold": 0.8 }
    }
  ]
}

Example Output (JSON list, top-2 only as relevant to "diabetes"):
[
  {"query": "diabetes diagnosis", "metadata": {"category": "diagnoses"}, "limit": 50, "threshold": 0.8},
  {"query": "hyperglycemia", "metadata": {"category": "diagnoses"}, "limit": 50, "threshold": 0.7}
]
"""