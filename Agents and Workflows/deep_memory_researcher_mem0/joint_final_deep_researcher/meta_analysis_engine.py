"""
Analysis Engine for Deep Memory Research Pipeline
Performs comprehensive meta-analysis of research artifacts and methodology
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from dotenv import load_dotenv

load_dotenv()

from rich import print as rprint

from camel.agents import ChatAgent
from camel.messages import BaseMessage
from camel.models import ModelFactory
from camel.types import ModelPlatformType, ModelType

from utils import load_artifact
from config.prompts import (
    ANALYSIS_SYSTEM_PROMPT,
    METHODOLOGY_ANALYSIS_PROMPT,
    DATA_QUALITY_ANALYSIS_PROMPT,
    FINDINGS_QUALITY_ANALYSIS_PROMPT,
    COMPREHENSIVE_ANALYSIS_PROMPT,
)

# this is like a weaver just before the final report that combines it all
# like metadat aartifact etc


class AnalysisEngine:
    """
    Comprehensive analysis engine that evaluates research methodology,
    quality, and findings across all pipeline artifacts
    """

    def __init__(self):
        rprint("Analysis engine initialized")
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        if not self.gemini_api_key:
            raise ValueError("Missing GEMINI_API_KEY in environment variables")

        # Use Gemini 2.5 Pro for comprehensive analysis
        self.model = ModelFactory.create(
            model_platform=ModelPlatformType.GEMINI,
            model_type=ModelType.GEMINI_2_5_PRO,
            api_key=self.gemini_api_key,
            model_config_dict={"temperature": 0.2, "max_tokens": 40000},
        )

        self.analysis_agent = ChatAgent(
            system_message=BaseMessage.make_assistant_message(
                role_name="ResearchAnalyst",
                content=ANALYSIS_SYSTEM_PROMPT,
            ),
            model=self.model,
        )

    def load_artifacts(self, artifacts_dict: Dict[str, str]) -> Dict[str, Any]:
        """Load all research artifacts for analysis"""
        loaded_artifacts = {}
        # loads on the fly artifacts such as metadata and plans etc to load into the final plan
        for artifact_type, file_path in artifacts_dict.items():
            try:
                loaded_artifacts[artifact_type] = load_artifact(file_path)
                rprint(f"Loaded {artifact_type}: {file_path}")
            except Exception as e:
                rprint(f"Failed to load {artifact_type}: {e}")
                loaded_artifacts[artifact_type] = {"error": str(e)}

        return loaded_artifacts

    def analyze_research_methodology(self, artifacts: Dict[str, Any]) -> str:
        """Analyze the research methodology and strategy"""

        metadata = artifacts.get("metadata", {})
        plan = artifacts.get("plan", {})
        search_list = artifacts.get("search_list", {})

        # this is cool for creating a great
        methodology_prompt = METHODOLOGY_ANALYSIS_PROMPT.format(
            metadata=json.dumps(metadata, indent=2),
            plan=json.dumps(plan, indent=2),
            search_list=json.dumps(search_list, indent=2),
        )

        response = self.analysis_agent.step(
            BaseMessage.make_user_message(role_name="User", content=methodology_prompt)
        )

        return response.msg.content

    def analyze_data_quality(self, artifacts: Dict[str, Any]) -> str:
        """Analyze data quality and search effectiveness"""

        raw_results = artifacts.get("raw_results", [])
        metadata = artifacts.get("metadata", {})

        # Calculate basic metrics
        total_searches = len([r for r in raw_results if r.get("search_query")])
        planned_searches = len(
            [r for r in raw_results if r.get("search_phase") == "planned"]
        )
        iterative_searches = len(
            [r for r in raw_results if r.get("search_phase") == "iterative"]
        )

        unique_memories = len(set(r.get("id", "") for r in raw_results if r.get("id")))
        avg_score = (
            sum(r.get("score", 0) for r in raw_results) / len(raw_results)
            if raw_results
            else 0
        )

        data_quality_prompt = DATA_QUALITY_ANALYSIS_PROMPT.format(
            total_searches=total_searches,
            planned_searches=planned_searches,
            iterative_searches=iterative_searches,
            unique_memories=unique_memories,
            avg_score=avg_score,
            raw_results_sample=json.dumps(raw_results[:5], indent=2),
            metadata=json.dumps(metadata, indent=2),
        )

        response = self.analysis_agent.step(
            BaseMessage.make_user_message(role_name="User", content=data_quality_prompt)
        )

        return response.msg.content

    def analyze_findings_quality(self, artifacts: Dict[str, Any], question: str) -> str:
        """Analyze the quality and consistency of research findings"""

        final_answer = artifacts.get("final_answer", "")
        raw_results = artifacts.get("raw_results", [])

        findings_prompt = FINDINGS_QUALITY_ANALYSIS_PROMPT.format(
            question=question,
            final_answer=final_answer,
            total_sources=len(raw_results),
            evidence_types=list(
                set(r.get("search_phase", "unknown") for r in raw_results)
            ),
        )

        response = self.analysis_agent.step(
            BaseMessage.make_user_message(role_name="User", content=findings_prompt)
        )

        return response.msg.content

    def generate_comprehensive_report(
        self,
        question: str,
        artifacts_dict: Dict[str, str],
        execution_time: float,
        session_id: str,
    ) -> str:
        """Generate comprehensive meta-analysis report"""

        artifacts = self.load_artifacts(artifacts_dict)

        methodology_analysis = self.analyze_research_methodology(artifacts)

        data_quality_analysis = self.analyze_data_quality(artifacts)

        findings_analysis = self.analyze_findings_quality(artifacts, question)

        # Generate final comprehensive report
        comprehensive_prompt = COMPREHENSIVE_ANALYSIS_PROMPT.format(
            session_id=session_id,
            question=question,
            execution_time=execution_time,
            artifacts_count=len(artifacts_dict),
            methodology_analysis=methodology_analysis,
            data_quality_analysis=data_quality_analysis,
            findings_analysis=findings_analysis,
            artifacts_details=json.dumps(artifacts_dict, indent=2),
        )

        rprint("Generating meta-analysis report...")
        response = self.analysis_agent.step(
            BaseMessage.make_user_message(
                role_name="User", content=comprehensive_prompt
            )
        )

        rprint("Meta-analysis complete")
        rprint(response.msg.content)

        return response.msg.content


def main():
    """Test the analysis engine"""
    import argparse

    parser = argparse.ArgumentParser(description="Research Analysis Engine")
    parser.add_argument("--question", required=True, help="Research question")
    parser.add_argument(
        "--artifacts", required=True, help="JSON file with artifact paths"
    )
    parser.add_argument(
        "--execution_time", type=float, default=0.0, help="Execution time"
    )
    parser.add_argument("--session_id", required=True, help="Session ID")

    args = parser.parse_args()

    # Load artifacts dictionary
    with open(args.artifacts, "r") as f:
        artifacts_dict = json.load(f)

    # Create analysis engine
    engine = AnalysisEngine()

    # Generate comprehensive report
    report = engine.generate_comprehensive_report(
        question=args.question,
        artifacts_dict=artifacts_dict,
        execution_time=args.execution_time,
        session_id=args.session_id,
    )

    rprint("\nComprehensive Analysis Report")
    rprint(report)


if __name__ == "__main__":
    main()
