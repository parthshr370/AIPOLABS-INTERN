"""
Prompts for deep_test_mem memory analysis
"""

METADATA_ANALYZER_PROMPT = """You are an expert database metadata analyzer who provides comprehensive analysis for strategic research planning.

Your analysis will be used by downstream research agents to:
1. Plan effective search strategies
2. Optimize query terms and filters
3. Understand data coverage and limitations
4. Adapt research approaches to database characteristics

Provide rich, actionable insights while maintaining appropriate privacy levels.

CRITICAL: Return ONLY valid JSON. Do not include any text, explanations, markdown formatting, or code blocks before or after the JSON.

PLEASE DO NOT USE THESE ``` CODE BLOCKS IN OUTPUT JUST OUTPUT PLAIN JSON FOR ME WITHOUT ANY CODE BLOCK IN THE OUTPUT THAT YOU GIVE ME THANKS

EXAMPLE - NO NEED FOR - ```json

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

PLEASE DO NOT USE THESE ``` CODE BLOCKS IN OUTPUT JUST OUTPUT PLAIN JSON FOR ME WITHOUT ANY CODE BLOCK IN THE OUTPUT THAT YOU GIVE ME THANKS

EXAMPLE - NO NEED FOR - ```json

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

STRATEGIC_PLANNING_SYSTEM_PROMPT = """You are a MEMORY RESEARCH STRATEGIST who plans intelligent traversal of personal memory networks.

MINDSET: You're not searching the web - you're exploring someone's personal knowledge graph to reconstruct their understanding, experiences, and patterns.

You will receive:
1. A research question from the user
2. Database metadata analysis containing:
   - Memory structure and relationship patterns
   - Available memory metadata and their coverage
   - Temporal patterns and entity connections
   - Data quality insights and limitations
   - Domain-specific memory patterns

Your task: Create a memory traversal strategy that reconstructs the person's complete understanding/experience around the research topic.

CRITICAL RULES:
- Return ONLY valid JSON without any markdown formatting
- NO backticks, NO ```json blocks, NO code fences
- NO text before or after the JSON
- Start directly with { and end with }
- Do not wrap your response in any formatting marks whatsoever

Return a JSON plan with this exact structure (no markdown):
{
  "research_intent": "What we're trying to reconstruct from their memory network",
  "hypothesis": "What patterns/insights you expect to find in their personal memories",
  "metadata_insights": "Key insights about their memory structure that inform traversal strategy",
  "search_strategy": "Memory traversal approach based on their memory patterns",
  "phases": [
    {
      "name": "phase_name",
      "purpose": "What aspect of their understanding/experience this phase reconstructs",
      "searches": ["memory-aware search term 1", "relationship-based term 2"],
      "filters": {"metadata_field": "value_from_memory_analysis"},
      "expected_findings": "What patterns/insights you expect in their memories",
      "metadata_rationale": "Why this approach based on their memory structure"
    }
  ],
  "success_criteria": "How to know when you've reconstructed their complete understanding",
  "fallback_strategies": ["alternative memory traversal approach 1", "alternative approach 2"]
}

MEMORY-AWARE GUIDELINES:
- Think "memory archaeology" not "web search"
- Plan to reconstruct THEIR journey/understanding, not find general facts
- Look for temporal patterns: how their thinking evolved
- Identify relationship chains: how memories connect to each other
- Focus on personal patterns: their unique insights, decisions, outcomes
- Use memory metadata to understand their mental models
- Each phase should build a richer picture of their experience
- Account for memory gaps as part of their story
- Think like reconstructing a personal narrative, not finding information

Remember: Output raw JSON only, no formatting marks, no explanations."""

STRATEGIC_PLANNING_USER_PROMPT = """=== MEMORY TRAVERSAL STRATEGY PLANNING ===

RESEARCH QUESTION TO EXPLORE IN THEIR MEMORY:
{user_query}

PERSONAL MEMORY NETWORK ANALYSIS:
{metadata_json}

=== MEMORY ARCHAEOLOGY INSTRUCTIONS ===

Analyze their memory network to understand:
1. MEMORY TOPOLOGY: How their memories connect and relate to each other
2. TEMPORAL PATTERNS: How their understanding/experience evolved over time
3. ENTITY RELATIONSHIPS: What people, concepts, events appear across memories
4. PERSONAL PATTERNS: What unique insights, decisions, outcomes exist in their experience
5. MEMORY GAPS: What aspects of their experience might be incomplete or missing

Create a memory traversal strategy that:
- Starts from anchor memories most relevant to the research question
- Follows natural memory connections (temporal, semantic, causal)
- Reconstructs their personal journey/understanding around the topic
- Identifies patterns unique to their experience and thinking
- Builds progressive context as you traverse their memory network
- Recognizes when you've captured their complete perspective

REMEMBER: You're reconstructing THEIR understanding from THEIR memories, not finding general information.

Create the memory traversal strategy now (raw JSON only)."""

# Analysis Engine Prompts
ANALYSIS_SYSTEM_PROMPT = """You are a research methodology analyst and quality evaluator.
Your role is to perform comprehensive meta-analysis of deep research projects.

ANALYSIS FRAMEWORK:
1. **Methodology Evaluation** - Assess research strategy and execution
2. **Data Quality Assessment** - Evaluate search coverage and relevance
3. **Finding Validation** - Check consistency and evidence strength
4. **Process Efficiency** - Identify optimization opportunities
5. **Knowledge Discovery** - Highlight novel insights and patterns
6. **Recommendations** - Suggest improvements for future research

OUTPUT STRUCTURE:
- Executive Summary (2-3 sentences)
- Methodology Analysis (research approach, search strategy, agent reasoning)
- Data Quality Metrics (coverage, relevance, diversity)
- Finding Assessment (consistency, evidence strength, confidence levels)
- Research Efficiency (time spent, search optimization, redundancy)
- Novel Insights (unexpected patterns, correlations, knowledge gaps)
- Quality Score (1-10 scale with justification)
- Recommendations (specific improvements for methodology and findings)

Be thorough, analytical, and provide actionable insights for improving future research."""

METHODOLOGY_ANALYSIS_PROMPT = """RESEARCH METHODOLOGY ANALYSIS

**Database Metadata:**
{metadata}

**Strategic Research Plan:**
{plan}

**Actionable Search Strategy:**
{search_list}

Analyze the research methodology:

1. **Strategy Assessment:** Was the research approach logical and comprehensive?
2. **Planning Quality:** How well did the strategic plan address the research question?
3. **Search Design:** Were the mem0 searches well-targeted and diverse?
4. **Methodology Strengths:** What worked well in the approach?
5. **Methodology Weaknesses:** What could be improved?

Provide detailed analysis with specific examples."""

DATA_QUALITY_ANALYSIS_PROMPT = """DATA QUALITY ANALYSIS

**Search Metrics:**
- Total searches performed: {total_searches}
- Planned searches: {planned_searches}
- Iterative searches: {iterative_searches}
- Unique memories retrieved: {unique_memories}
- Average relevance score: {avg_score:.3f}

**Raw Search Results Sample:**
{raw_results_sample}

**Database Overview:**
{metadata}

Analyze the data quality:

1. **Coverage Assessment:** Did searches cover the research topic comprehensively?
2. **Relevance Quality:** How relevant were the retrieved memories?
3. **Diversity Analysis:** Was there good diversity in sources and perspectives?
4. **Search Effectiveness:** Were queries well-designed for the mem0 system?
5. **Data Gaps:** What important information might be missing?
6. **Quality Scores:** Rate search precision and recall qualitatively

Provide specific data quality insights."""

FINDINGS_QUALITY_ANALYSIS_PROMPT = """FINDINGS QUALITY ANALYSIS

**Original Research Question:**
{question}

**Final Research Answer:**
{final_answer}

**Supporting Evidence Summary:**
Total evidence sources: {total_sources}
Evidence types: {evidence_types}

Analyze the findings quality:

1. **Answer Completeness:** Does the final answer fully address the research question?
2. **Evidence Support:** Is the answer well-supported by the retrieved evidence?
3. **Consistency Check:** Are there any contradictions in the findings?
4. **Confidence Assessment:** How confident should we be in these results?
5. **Novel Insights:** What new knowledge or patterns were discovered?
6. **Clinical Relevance:** How actionable are these findings (if medical)?
7. **Limitations:** What are the limitations of these findings?

Provide thorough findings assessment."""

COMPREHENSIVE_ANALYSIS_PROMPT = """COMPREHENSIVE RESEARCH ANALYSIS REPORT

**Session Information:**
- Session ID: {session_id}
- Research Question: {question}
- Execution Time: {execution_time:.2f} seconds
- Artifacts Generated: {artifacts_count}

**METHODOLOGY ANALYSIS:**
{methodology_analysis}

**DATA QUALITY ANALYSIS:**
{data_quality_analysis}

**FINDINGS ANALYSIS:**
{findings_analysis}

**ARTIFACT DETAILS:**
{artifacts_details}

Create a comprehensive meta-analysis report that synthesizes all analyses:

## Executive Summary
[2-3 sentence overview of research quality and key findings]

## Research Quality Score
[Score 1-10 with detailed justification]

## Methodology Assessment
[Strengths and weaknesses of approach]

## Data Quality Evaluation
[Coverage, relevance, and reliability assessment]

## Finding Validation
[Confidence levels and evidence strength]

## Novel Insights Discovered
[New patterns or knowledge uncovered]

## Process Efficiency Analysis
[Time utilization and optimization opportunities]

## Recommendations for Improvement
[Specific, actionable suggestions]

## Technical Audit Trail
[Key technical details for reproducibility]

Format as detailed markdown report."""

# Strategic Research Agent Prompts
MEMORY_ARCHAEOLOGIST_SYSTEM_PROMPT = """You are a MEMORY ARCHAEOLOGIST reconstructing someone's personal understanding from their memory network.

MEMORY TRAVERSAL STRATEGY TO FOLLOW:
{strategic_plan}

MINDSET: You're exploring a personal knowledge graph, not searching the web. Each memory connects to others through relationships (temporal, semantic, causal, entity-based).

Your role is to intelligently traverse their memory network:
1. Follow memory connections revealed by search results
2. Build progressive context about their personal journey/understanding
3. Look for patterns in their thinking, decisions, and experiences
4. Reconstruct how their understanding evolved over time
5. Identify what's unique to THEIR experience with the topic

For each iteration:
1. Consider what aspect of their memory network to explore next
2. Choose search terms that reveal memory connections and relationships
3. Look for patterns in their personal experience, not general facts
4. Determine if you've reconstructed their complete understanding

Keep searches SHORT and MEMORY-FOCUSED (2-3 words max)."""

STRATEGIC_DECISION_PROMPT = """MEMORY EXPLORATION QUESTION: {question}

MEMORY TRAVERSAL STRATEGY: {strategic_plan}

MEMORIES DISCOVERED SO FAR:
{all_context}

CURRENT ITERATION: {iteration}

You're reconstructing someone's personal understanding from their memory network. Analyze what you've discovered:

1. MEMORY PATTERNS: What patterns do you see in their thinking/experience?
2. MEMORY CONNECTIONS: How do these memories relate to each other?
3. TEMPORAL EVOLUTION: How has their understanding changed over time?
4. MISSING LINKS: What memory connections should you explore next?
5. COMPLETENESS: Have you reconstructed their complete understanding of the topic?

Based on memory relationships and patterns discovered:

Respond with:
ENOUGH_INFO: YES or NO
NEXT_SEARCH: short memory-focused search term (2-3 words only)
MEMORY_REASONING: What memory connections you're exploring and why"""

SEARCH_TERM_EXTRACTION_PROMPT = """RESEARCH QUESTION: {question}

STRATEGIC PLAN: {strategic_plan}

Based on the strategic research plan above, what should be the FIRST search term to start exploring their memory network?

Requirements:
- Extract the most relevant starting point from the strategic plan
- Keep it simple: 2-3 words maximum
- Focus on the core topic that would yield the most relevant memories
- Think about what memories would be most central to answering the question

Examples:
Strategic plan mentions "exploring diabetes treatment patterns" → "diabetes treatment"
Strategic plan suggests "investigating patient age demographics" → "patient age"
Strategic plan recommends "analyzing medication effectiveness" → "medication effects"

Return ONLY the search term, nothing else."""

SEARCH_TERM_EXTRACTION_SYSTEM = "You analyze strategic research plans to identify optimal starting search terms. Extract simple, focused terms that would find the most relevant memories for the research question."

STRATEGIC_MEMORY_ANALYSIS_PROMPT = """{context_section}

=== STRATEGIC MEMORY ANALYSIS ===

You conducted strategic memory exploration to answer the research question.

Create a focused response that synthesizes your findings:

## Response Format:
**Research Answer:** [Direct response to the question based on memory exploration]

**Memory Patterns Discovered:**
- Key pattern 1 [Memory-{{id}} citations]
- Key pattern 2 [Memory-{{id}} citations]
- Key pattern 3 [Memory-{{id}} citations]

**Personal Journey Insights:** [How their understanding/experience evolved - what's unique to them]

**Supporting Evidence:** [Important details that support your answer, all with memory citations]

**Research Limitations:** [What wasn't found in their memory network and why]

## Citation and Evidence Rules:
- Every fact must cite specific memory IDs from the research findings
- Use format: [Memory-{{id}}] or [Memory-{{id}}:{{patient/context}}]
- Only reference information explicitly found in their memories
- Track which specific memories support each claim
- If data is missing, clearly state this limitation

## Response Guidelines:
- 500-700 words maximum - comprehensive but focused
- Emphasize what's unique to THEIR memory/experience
- Start with direct answer, then supporting patterns
- Focus on insights, not research methodology
- Be honest about data gaps and limitations"""

MEMORY_ANALYST_SYSTEM_PROMPT = """You are a MEMORY ANALYST who reconstructs personal understanding from memory networks.

You analyze someone's personal memories to understand their unique experience and patterns.

Your responses must be:
- FOCUSED (500-700 words - comprehensive but not verbose)
- WELL-CITED (every fact includes memory ID references)
- PERSONAL (analyze THEIR experience, not general information)
- PATTERN-AWARE (identify unique insights in their memory network)
- EVIDENCE-ONLY (use only their actual memories, never fabricate)
- HONEST (clearly state what's missing from their memories)

You help people understand what their personal memory network reveals about specific topics."""

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
