import json
from typing import List, Optional

from camel.agents import ChatAgent
from camel.messages import BaseMessage
from pydantic import BaseModel, Field, ValidationError
from rich.console import Console
from rich.panel import Panel

from config import (
    GEMINI_API_KEY,
    MAX_CONTEXT_LENGTH,
    MAX_RESEARCH_STEPS,
    USER_ID,
)
from memory_interface import MemoryInterface
from utils import load_prompt, parse_json_from_response, create_llm_agent


class ResearchStep(BaseModel):
    step: int = Field(..., description="The step number in the research plan.")
    action: str = Field(..., description="The type of search to perform (e.g., SEARCH_BROAD, SEARCH_FOCUSED).")
    query: str = Field(..., description="The specific search query for this step.")
    rationale: str = Field(..., description="The reasoning behind this research step.")


class ResearchPlan(BaseModel):
    original_query: str = Field(..., description="The user's original research query.")
    research_questions: List[str] = Field(default_factory=list, description="A list of questions to answer.")
    research_steps: List[ResearchStep] = Field(default_factory=list, description="A detailed plan of research steps.")


class AnalysisResult(BaseModel):
    summary: str = Field(..., description="A high-level summary of the findings.")
    key_insights: List[str] = Field(default_factory=list, description="A list of key insights discovered.")
    patterns: List[str] = Field(default_factory=list, description="A list of patterns or trends identified.")
    evidence: List[str] = Field(default_factory=list, description="A list of evidence or data points supporting the findings.")


class Metadata(BaseModel):
    key_concepts: List[str] = Field(
        default_factory=list,
        description="List of key concepts or entities found in the memory silo.",
    )
    dominant_themes: List[str] = Field(
        default_factory=list,
        description="Dominant themes or topics that emerge from the data.",
    )
    data_distribution: dict = Field(
        default_factory=dict,
        description="High-level statistics on data types or categories.",
    )


class DeepResearchAgent:
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.console = Console()
        self.memory_interface = MemoryInterface()
        self.research_context = ""
        self.llm_agent = create_llm_agent()

    def run(self, query: str):
        self.console.print(
            Panel(
                f"[bold blue]🧠 Deep Memory Researcher[/bold blue]\n\n"
                f"Query: {query}\n"
                f"User ID: {self.user_id}",
                title="🔬 Medical Research Orchestrator",
                border_style="green",
            )
        )

        # Step 1: Create metadata (can be run async in a real system)
        metadata = self._create_metadata()

        # Step 2: Create a detailed research plan
        plan = self._create_research_plan(query, metadata)
        if not plan:
            self.console.print("[red]❌ Failed to create a research plan. Aborting.[/red]")
            return

        # Steps 3-5: Execute the research loop
        raw_data = self._execute_research_loop(plan)
        if not raw_data:
            self.console.print("[red]❌ Research loop failed to produce data. Aborting.[/red]")
            return

        # Step 6: Analyze the raw data
        analysis = self._analyze_data(raw_data)
        if not analysis:
            self.console.print("[red]❌ Data analysis failed. Aborting.[/red]")
            return

        # Step 7: Generate the final report
        report = self._generate_report(metadata, analysis, raw_data)
        self.console.print(Panel(report, title="📄 Final Report", border_style="green"))
        return report

    def _create_metadata(self) -> Optional[Metadata]:
        self.console.print("\n[bold cyan]STEP 1: METADATA INGESTION[/bold cyan]")
        all_memories = self.memory_interface.get_all(self.user_id, limit=1000)
        if not all_memories:
            self.console.print("[yellow]No memories found for this user.[/yellow]")
            return Metadata()

        prompt = load_prompt("METADATA_ANALYZER").format(
            memory_silo="\n".join([mem["memory"] for mem in all_memories])
        )

        response = self.llm_agent.step(
            BaseMessage.make_user_message(role_name="User", content=prompt)
        )
        parsed_json = parse_json_from_response(response.msg.content)

        if not parsed_json:
            self.console.print(
                "[yellow]LLM failed to return structured metadata. Using empty metadata.[/yellow]"
            )
            return Metadata()

        try:
            return Metadata.parse_obj(parsed_json)
        except ValidationError as e:
            self.console.print(f"[red]Metadata validation failed: {e}[/red]")
            return Metadata()

    def _create_research_plan(
        self, query: str, metadata: Optional[Metadata]
    ) -> Optional[ResearchPlan]:
        self.console.print("\n[bold cyan]STEP 2: QUERY PROCESSING[/bold cyan]")
        metadata_content = metadata.model_dump_json(indent=2) if metadata else "{}"

        prompt = load_prompt("QUERY_PROCESSOR").format(
            query=query, metadata=metadata_content
        )

        response = self.llm_agent.step(
            BaseMessage.make_user_message(role_name="User", content=prompt)
        )
        parsed_json = parse_json_from_response(response.msg.content)

        if not parsed_json:
            self.console.print(
                "[red]LLM failed to return a structured research plan.[/red]"
            )
            return None

        try:
            # Ensure the original query is part of the plan
            parsed_json["original_query"] = query
            return ResearchPlan.parse_obj(parsed_json)
        except ValidationError as e:
            self.console.print(f"[red]Research plan validation failed: {e}[/red]")
            return None

    def _execute_research_loop(self, plan: ResearchPlan) -> str:
        self.console.print("\n[bold cyan]STEPS 3-5: REWOO-REACT SEARCH LOOP[/bold cyan]")
        planner_agent = create_llm_agent(
            load_prompt("RESEARCH_PLANNER"), temperature=0.0
        )
        observer_agent = create_llm_agent(
            load_prompt("RESEARCH_OBSERVER"), temperature=0.0
        )

        for step in range(MAX_RESEARCH_STEPS):
            self.console.print(f"\n[bold magenta]--- Research Step {step + 1} ---[/bold magenta]")

            # 1. REASON about the next search
            reasoning_prompt = f"Based on the plan and current context, what is the next logical search query? Plan: {plan.model_dump_json()}, Context: {self.research_context}"
            reasoning_response = planner_agent.step(
                BaseMessage.make_user_message("User", reasoning_prompt)
            )
            search_query = reasoning_response.msg.content.strip()
            self.console.print(f"[cyan]🧠 Reasoning complete. Next query: {search_query}[/cyan]")

            # 2. ACT by executing the search
            search_results = self.memory_interface.progressive_search(
                search_query, self.user_id
            )

            # 3. OBSERVE the results and update context
            observation_prompt = f"Query: {search_query}\nResults: {search_results}\nBased on these, what are the key insights and should we continue?"
            observation_response = observer_agent.step(
                BaseMessage.make_user_message("User", observation_prompt)
            )
            observation = observation_response.msg.content.strip()

            # Accumulate data
            self.research_context += f"\n\n--- Step {step + 1} ---\nQuery: {search_query}\nObservation: {observation}"

            # Trim context to avoid excessive length
            if len(self.research_context) > MAX_CONTEXT_LENGTH:
                self.research_context = self.research_context[-MAX_CONTEXT_LENGTH:]

            self.console.print(f"[green]✅ Observation complete. Context updated.[/green]")

            # Simple stop condition for this example
            if "continue: no" in observation.lower():
                break

        return self.research_context

    def _analyze_data(self, raw_data: str) -> Optional[AnalysisResult]:
        self.console.print("\n[bold cyan]STEP 6: DATA ANALYSIS[/bold cyan]")
        prompt = load_prompt("DATA_ANALYZER").format(raw_data=raw_data)

        response = self.llm_agent.step(
            BaseMessage.make_user_message(role_name="User", content=prompt)
        )
        parsed_json = parse_json_from_response(response.msg.content)

        if not parsed_json:
            self.console.print("[red]LLM failed to return structured analysis.[/red]")
            return None

        try:
            return AnalysisResult.parse_obj(parsed_json)
        except ValidationError as e:
            self.console.print(f"[red]Analysis validation failed: {e}[/red]")
            return None

    def _generate_report(
        self,
        metadata: Optional[Metadata],
        analysis: AnalysisResult,
        raw_data: str,
    ) -> str:
        self.console.print("\n[bold cyan]STEP 7: REPORT GENERATION[/bold cyan]")
        prompt = load_prompt("REPORT_SYNTHESIZER").format(
            metadata=metadata.model_dump_json(indent=2) if metadata else "{}",
            analysis=analysis.model_dump_json(indent=2),
            raw_data=raw_data,
        )

        response = self.llm_agent.step(
            BaseMessage.make_user_message(role_name="User", content=prompt)
        )
        return response.msg.content
