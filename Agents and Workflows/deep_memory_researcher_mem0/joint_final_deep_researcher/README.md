# Deep Memory Research Pipeline

A comprehensive autonomous research system that transforms your `mem0` memories into publication-quality research reports through strategic multi-phase analysis.

## Overview

This system conducts deep, systematic research on your mem0 database by combining strategic planning with iterative investigation. It produces comprehensive, evidence-based research reports suitable for medical journals or professional presentations.

**Input:** Research question + mem0 database  
**Output:** Detailed research report with full methodology audit trail

## Quick Start

```bash
# Run the complete pipeline
python main.py
```

**Interactive prompts:**
```
Deep Memory Research Pipeline
==================================================
I'll help you research your mem0 memories comprehensively!

What would you like to research? [Enter your question here]
```

**Fixed Settings:**
- User ID: `doctor_memory`
- Max Memories: `100`

## Project Structure

```
deep-memory-researcher/
├── main.py                      # Main pipeline orchestrator
├── metadata_generator.py        # Phase 1: Database metadata analysis
├── rewoo_planner.py            # Phase 2: ReWOO strategic planning
├── strategic_react_agent.py    # Phase 3: Strategic ReAct research agent
├── meta_analysis_engine.py     # Phase 4: Meta-analysis and quality evaluation
├── utils.py                     # Utilities and artifact management
├── artifacts/                   # Generated research reports
├── config/
│   └── prompts.py              # All LLM prompts
├── docs/
│   └── STATE.md                # mem0 API reference
└── requirements.txt            # Dependencies
```

## Pipeline Architecture

The system runs a **4-phase autonomous pipeline:**

### **Phase 1: Database Metadata Analysis** (`metadata_generator.py`)
- Analyzes mem0 database structure and content patterns
- Generates comprehensive metadata overview using CAMEL AI
- Identifies data completeness, themes, and research opportunities
- **Output:** `metadata.json`

### **Phase 2: Strategic Research Planning** (`rewoo_planner.py`)
- Creates multi-phase investigation strategy using ReWOO methodology
- Plans research approach based on database characteristics
- Defines phases, search strategies, and success criteria
- **Output:** `plan.json`

### **Phase 3: Strategic Deep Research Execution** (`strategic_react_agent.py`)
- Executes iterative mem0 searches guided by strategic plan
- Uses enhanced ReAct with strategic plan guidance
- Adapts search strategy based on findings and memory connections
- **Output:** `final_answer.md` + `raw_results.jsonl`

### **Phase 4: Comprehensive Meta-Analysis** (`meta_analysis_engine.py`)
- Analyzes research methodology and data quality
- Validates findings and identifies limitations
- Generates quality scores and improvement recommendations
- **Output:** `analysis_report.md`

## Generated Artifacts

Every research session creates timestamped artifacts in `artifacts/`:

```
YYYYMMDD_HHMM_metadata.json      - Database structure analysis
YYYYMMDD_HHMM_plan.json          - Strategic research plan  
YYYYMMDD_HHMM_final_answer.md    - Comprehensive research report (1000-1500+ words)
YYYYMMDD_HHMM_raw_results.jsonl  - Complete search audit trail
YYYYMMDD_HHMM_analysis_report.md - Meta-analysis and quality evaluation
```

## Technical Architecture

### **Key Technologies**
- **mem0 SDK** - Memory database operations
- **CAMEL AI Framework** - LLM agent orchestration
- **Google Gemini** - LLM processing (2.5 Pro for research, Flash-Lite for analysis)
- **Rich** - Terminal output formatting
- **Python 3.8+** - Runtime environment

### **Research Methodologies**

**Strategic Planning (ReWOO)**
- Plan everything upfront, then execute systematically
- Multi-phase research strategy based on database characteristics
- Structured JSON plan with phases, searches, and success criteria

**Iterative Research (Enhanced ReAct)**
- Adaptive reasoning where strategic plan guides each decision
- Plan-informed iterative searches with CAMEL AI reasoning
- Strategic guidance, evidence-based stopping, comprehensive reporting

**Meta-Analysis Engine**
- Research Quality Scoring - Evaluates methodology and findings (1-10 scale)
- Data Quality Assessment - Analyzes coverage, relevance, and reliability
- Finding Validation - Checks for fabrication and evidence strength
- Methodology Evaluation - Reviews research approach effectiveness

## Configuration

### **Environment Variables**
Required in `.env` file:
```bash
MEM0_API_KEY=your_mem0_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
```

### **Default Settings**
- **User ID:** `doctor_memory` (fixed)
- **Max Memories:** `100` (fixed) 
- **Model:** Gemini 2.5 Pro for research, Flash-Lite for metadata
- **Temperature:** 0.2 for research, 0.3 for analysis
- **Max Iterations:** 5 per research phase

## Example Research Questions

### **Medical Research**
```
"What are my most effective diabetes treatments?"
"How many patients have chronic pain and what are their demographics?"
"What treatment effectiveness patterns exist in my practice?"
"What are the common side effects across all medications?"
```

### **Pattern Discovery**
```
"What trends exist in patient outcomes over the past year?"
"Which diagnostic approaches show the best accuracy?"
"What are the most common comorbidities in my patient population?"
```

### **Clinical Analytics**
```
"What factors correlate with successful treatment outcomes?"
"How do patient demographics influence treatment response?"
"What are the most challenging cases and their characteristics?"
```

## Quality Assurance

### **Built-in Safeguards**
- **Evidence-Only Reporting** - Never fabricates data not present
- **Clear Limitation Statements** - Explicitly states data gaps
- **Source Attribution** - All findings traceable to specific memories
- **Quality Scoring** - Automatic evaluation of research methodology

### **Research Integrity Features**
- **Complete Audit Trail** - Every search and decision logged
- **Methodology Transparency** - Strategic plan execution documented
- **Self-Evaluation** - Analysis engine provides quality feedback
- **Reproducibility** - All artifacts preserved for verification

## Limitations and Considerations

### **Current Limitations**
- **Fixed to mem0 Platform** - Currently designed for mem0 databases only
- **English Language** - Optimized for English medical terminology
- **Gemini Dependency** - Requires Google Gemini API access
- **Medical Domain Focus** - Prompts optimized for medical/clinical data

### **Data Quality Dependencies**
- **Metadata Richness** - Better results with well-structured mem0 metadata
- **Memory Completeness** - Gaps in memory data affect research quality
- **Search Term Effectiveness** - Results depend on semantic similarity matching

## License

This project is designed for medical research and clinical decision support. Ensure compliance with healthcare data regulations (HIPAA, GDPR) when processing patient information.

---

## Research Impact

This system transforms scattered medical memories into structured knowledge through:
- **Systematic Investigation** - Strategic, evidence-based research methodology
- **Comprehensive Analysis** - Deep pattern recognition and insight extraction  
- **Quality Assurance** - Built-in validation and limitation identification
- **Professional Reporting** - Publication-quality research documentation

**Perfect for medical practitioners, researchers, and healthcare organizations seeking to unlock insights from their memory databases.**

---

*Last updated: August 13, 2024*  
*Version: 2.0 - Clean & Organized Deep Memory Research Pipeline*