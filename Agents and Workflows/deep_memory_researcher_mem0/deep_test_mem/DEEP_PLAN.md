# Deep Research Agent for Mem0 – Comprehensive Development Plan

> **File:** `DEEP_PLAN.md`  
> **Purpose:** Road-map for converting the current prototype (in `deep_test_mem/`) into a fully–functional, end-to-end **Deep Research Agent** as described by the user.

---

## 0. Vision

Create a single **autonomous pipeline** that, given only:

* `user_id` – whose memories we analyse (e.g. `doctor_memory`)
* `prompt`  – natural-language research question

returns a **grounded, well-structured answer** by:
1. Retrieving relevant memories from Mem0
2. Iteratively reasoning / searching until information is sufficient
3. Producing a final analytical report (plus all intermediate artefacts)

All steps must be **automated, robust, and easily extensible**.

---

## 1. Current Assets & Issues

| Component | Status | Re-use? | Notes |
|-----------|--------|---------|-------|
| `metadata_ingestion.py` | ✅ Works but path fixes needed | ✔ | Generates metadata JSON from `mem0.get_all()` sample. |
| `rewoo_research_planner.py` | ✅ Works (needs path fixes) | ✔ | Creates strategic multi-phase plan from metadata + question. |
| `test_react.py` (`decompose_plan_to_searches`) | ✅ Works | ✔ | Converts plan → list of actionable `mem0.search()` calls. |
| `simple_loop_agent.py` | ✅ Works standalone | ✔ | Executes iterative `mem0.search` loop & synthesises answer. |
| `iterative_react_agent.py` | Alternative implementation | △ | More verbose; keep for reference. |
| `simple_react_agent.py` | ReAct style | △ | Might merge ideas later. |
| `STATE.md` | Diagnostic notes | ✔ | Keep as reference. |

**Global problems** (already noted in `STATE.md`):
1. `sys.path` hacks for `camel/` and `mem0/` – fragile.
2. `load_dotenv()` order wrong in a few files.
3. Phases 1 & 2 are **not wired together**.
4. No persistence folder for artefacts.
5. No master orchestrator (`main.py`) doing all steps serially.

---

## 2. Target Architecture (One-Pass Pipeline)

```mermaid
graph TD
    A((User Prompt))
    A --> B{{Orchestrator<br/>`main.py`}}
    subgraph Phase-1  [ Analyse DB & Plan ]
        B --> C[Metadata Ingestion<br/>`metadata_ingestion.get_database_metadata()`]
        C -->|metadata.json| D[Strategic Planner<br/>`ReWOOResearchPlanner.create_research_plan()`]
        D -->|plan.json| E[Plan Decomposer<br/>`decompose_plan_to_searches()`]
    end
    subgraph Phase-2 [ Deep Research Loop ]
        E -->|search_list| F[Search Executor<br/>`SimpleLoopAgent`]
        F -->|final_answer.md| G[Artefact Saver]
    end
    subgraph Phase-3 [ Synthesis & Audit ]
        C -.-> G
        D -.-> G
        E -.-> G
        F -.-> G
        G --> H[Analysis Engine (LLM)]
        H --> I((Comprehensive Report))
    end
```

### Folder / File Layout

```
deep_test_mem/
│
├── orchestrator/
│   ├── main.py              # <–– new master script (CLI)
│   ├── artefacts/           # auto-created; holds all JSON / reports
│   │   ├── YYYYMMDD_HHMM_metadata.json
│   │   ├── YYYYMMDD_HHMM_plan.json
│   │   ├── YYYYMMDD_HHMM_search_list.json
│   │   ├── YYYYMMDD_HHMM_raw_results.jsonl
│   │   └── YYYYMMDD_HHMM_final_answer.md
│   └── analysis_engine.py   # optional deep audit using Camel agent
│
├── metadata_ingestion.py    # kept (minor fixes)
├── rewoo_research_planner.py# kept (minor fixes)
├── plan_decomposer.py       # renamed from test_react.py for clarity
├── simple_loop_agent.py     # kept (rename functions for clarity)
└── utils.py                 # path + logging helpers
```

---

## 3. Implementation Steps

### Phase A – Refactor & Fixes
1. **Path Handling**
   * Add a small `utils.py` with:
     ```python
     import pathlib, sys
     ROOT = pathlib.Path(__file__).resolve().parents[1]  # project root
     sys.path.append(str(ROOT / "camel"))
     sys.path.append(str(ROOT / "mem0"))
     ```
   * Import this early in every script OR centralise inside the new `main.py` & others just `from utils import ROOT`.
2. **Env Loading** – enforce:
   ```python
   from dotenv import load_dotenv; load_dotenv()
   ```
   *before* any `os.getenv` calls.
3. **Rename `test_react.py` → `plan_decomposer.py`** for semantics.
4. **Black / Ruff lint sweep** (optional).

### Phase B – Orchestrator (`main.py`)
1. CLI using `argparse` with arguments: `--user_id`, `--question`, `--max_memories` (optional).
2. Pipeline steps (sequential):
   ```python
   # 1. metadata
   metadata_json = get_database_metadata(user_id=args.user_id, limit=args.max_memories)
   save("metadata", metadata_json)

   # 2. strategic plan
   plan_json = planner.create_research_plan(question, metadata_json)
   save("plan", plan_json)

   # 3. actionable search list
   search_list_json = decompose_plan_to_searches(plan_json)
   save("search_list", search_list_json)

   # 4. execute deep search
   answer_md, raw_results = SimpleLoopAgent().execute_from_search_list(question, search_list_json)
   save("raw_results", raw_results, ext="jsonl")
   save("final_answer", answer_md, ext="md")
   ```
3. Return / print final answer nicely with Rich.

### Phase C – Enhance `SimpleLoopAgent`
1. Add new method `execute_from_search_list(question, search_list_json)` that:
   * Iterates through provided list instead of self-refinement **first**.
   * Falls back to internal refinement loop if list becomes exhausted without answer.
2. Collects **all** search results into JSONL for audit.
3. Uses existing analysis / synthesis functions for final answer.

### Phase D – Analysis Engine (Optional but Requested)
1. Create `analysis_engine.py` with a Camel ChatAgent taking as **system prompt** the evaluation rubric (metadata, plan, answer, etc.) and producing a Markdown report.
2. Run it at the end of `main.py`; save to `artefacts/analysis_report.md`.

### Phase E – Persistence Helper
Implement `save(kind, data_str, ext="json")` inside `utils.py` that:
```python
from datetime import datetime, timezone; import pathlib
TS = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
fname = ARTEFACTS_DIR / f"{TS}_{kind}.{ext}"
with open(fname, "w", encoding="utf-8") as f:
    f.write(data_str)
```

### Phase F – Testing & Validation
1. Add `tests/test_orchestrator.py` that mocks Mem0 client to return predictable data and asserts full pipeline produces non-empty answer.
2. Provide sample `.env.example` with expected keys.

---

## 4. Design Decisions & Rationale
* **Reuse over Re-write** – keep existing LLM prompts & Camel agents (they already work) → faster delivery.
* **LLM JSON Parsing** – offload heavy JSON sanity to LLM but keep lightweight `json.loads` where needed (planner/decomposer already output JSON-safe by prompt design).
* **Artefact Persistence** – deterministic timestamp naming → easy diffing & audit across runs.
* **Decoupled Phases** – each phase outputs plain strings/files → easy to swap any component.
* **Extensibility** – future: plug in Pinecone, Elasticsearch, or switch to other LLMs by editing `ModelFactory` config only.

---

## 5. Milestones & Timeline (suggested)
| Week | Deliverable |
|------|-------------|
| 1 | Phase A refactor & all imports/env fixed. ✅ Scripts run standalone. |
| 2 | Phase B orchestrator end-to-end happy path (no analysis engine). |
| 3 | Phase C better `SimpleLoopAgent` + raw result storage. |
| 4 | Phase D analysis engine & rich report. |
| 5 | Phase E tests, docs, polish, README update. |

---

## 6. Open Questions
1. Should the analysis engine use **the same model** as research or a cheaper reviewer model?
2. Desired output format for final answer – Markdown or structured JSON?
3. Any privacy constraints on writing patient names into artefacts?

---

## 7. Immediate Next Actions (for this repo)
1. **Create `orchestrator/` folder & scaffold `main.py`.**
2. Move / rename `test_react.py` → `plan_decomposer.py`.
3. Add `utils.py` with path helper + save helper.
4. Fix `load_dotenv` placement in all current scripts.
5. Run first manual end-to-end test.

---

*End of plan – ready for implementation.*
