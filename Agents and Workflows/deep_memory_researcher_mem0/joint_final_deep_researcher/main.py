#!/usr/bin/env python3
"""
Deep Memory Research Pipeline Orchestrator
Complete autonomous pipeline: metadata -> plan -> search -> research -> analysis
"""

import json
import sys
import time
from pathlib import Path
from typing import Dict, Any

# Add parent directory to path to import modules
sys.path.append(str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

from rich import print as rprint

# Import our pipeline components
from utils import save_artifact, save_jsonl_artifact, get_timestamp, load_artifact
from metadata_generator import get_database_metadata, get_filtered_memory
from rewoo_planner import ReWOOResearchPlanner  
from strategic_react_agent import StrategicResearchAgent
from meta_analysis_engine import AnalysisEngine
from memory_writer import write_memories_from_reports


class DeepResearchOrchestrator:
    """Main orchestrator for the deep research pipeline"""
    
    def __init__(self, user_id: str = "doctor_memory", max_memories: int = 100):
        self.user_id = user_id
        self.max_memories = max_memories
        self.session_timestamp = get_timestamp()
        self.artifacts = {}  # Store paths to all generated artifacts
        
        rprint(f"Pipeline initialized - Session: {self.session_timestamp}")
    
    def phase_1_metadata_analysis(self) -> str:
        """Phase 1: Analyze database and generate metadata"""
        rprint("\nPhase 1: Database Analysis")
        
        # Load filtered memories
        filtered_memories = get_filtered_memory(
            user_id=self.user_id, 
            limit=self.max_memories
        )
        rprint(f"Loaded {len(filtered_memories)} memories")
        
        # Generate metadata analysis
        metadata_json = get_database_metadata(filtered_memory=filtered_memories)
        
        if not metadata_json:
            raise ValueError("Failed to generate metadata analysis")
            
        # Save metadata artifact
        metadata_path = save_artifact("metadata", metadata_json, ext="json")
        self.artifacts["metadata"] = metadata_path
        
        rprint(f"Metadata analysis saved: {metadata_path}")
        
        return metadata_json
    
    def phase_2_strategic_planning(self, question: str, metadata_json: str) -> str:
        """Phase 2: Create strategic research plan"""
        rprint("\nPhase 2: Strategic Planning")
        
        # Initialize ReWOO planner
        planner = ReWOOResearchPlanner()
        
        # Create research plan
        research_plan = planner.create_research_plan(question, metadata_json)
        
        if "error" in research_plan.lower():
            raise ValueError("Failed to create research plan")
        
        # Save plan artifact  
        plan_path = save_artifact("plan", research_plan, ext="json")
        self.artifacts["plan"] = plan_path
        
        rprint(f"Research plan saved: {plan_path}")
        
        return research_plan
    
    def phase_3_plan_decomposition(self, research_plan: str) -> str:
        """Phase 3: Decompose plan into actionable searches"""
        rprint("\nPhase 3: Deep Research")
        
        # Decompose plan into mem0 searches
        search_list_json = decompose_plan_to_searches(research_plan)
        
        # Save search list artifact
        search_list_path = save_artifact("search_list", search_list_json, ext="json")
        self.artifacts["search_list"] = search_list_path
        
        rprint(f"Search list saved: {search_list_path}")
        
        return search_list_json
    
    def phase_3_strategic_deep_research(self, question: str, strategic_plan: str, metadata_context: str) -> tuple:
        """Phase 3: Execute strategic deep research loop with full context"""
        rprint("\nPhase 3: Strategic Deep Research")
        
        # Initialize research agent
        agent = StrategicResearchAgent()
        
        # Execute strategic research with full context (plan + metadata guides iterative agent)
        final_answer, raw_results = agent.execute_with_strategic_plan(question, strategic_plan, metadata_context)
        
        # Save artifacts
        final_answer_path = save_artifact("final_answer", final_answer, ext="md")
        raw_results_path = save_jsonl_artifact("raw_results", raw_results)
        
        self.artifacts["final_answer"] = final_answer_path
        self.artifacts["raw_results"] = raw_results_path
        
        rprint(f"Final research report saved to: {final_answer_path}")
        rprint(f"Raw search results saved to: {raw_results_path}")
        
        return final_answer, raw_results
    
    def phase_4_comprehensive_analysis(self, question: str, execution_time: float) -> str:
        """Phase 4: Create comprehensive meta-analysis report"""
        rprint("\nPhase 4: Meta-Analysis")
        
        # Initialize analysis engine
        analysis_engine = AnalysisEngine()
        
        # Generate comprehensive meta-analysis report
        analysis_report = analysis_engine.generate_comprehensive_report(
            question=question,
            artifacts_dict=self.artifacts,
            execution_time=execution_time,
            session_id=self.session_timestamp
        )
        
        # Save analysis report
        analysis_path = save_artifact("analysis_report", analysis_report, ext="md")
        self.artifacts["analysis_report"] = analysis_path
        
        rprint(f"Analysis report saved: {analysis_path}")
        
        return analysis_report
    
    def phase_5_memory_writing(self, question: str) -> int:
        """Phase 5: Extract insights and write to memory (optional)"""
        rprint("\nPhase 5: Memory Writing")
        
        # Load the reports from artifacts
        final_answer_path = self.artifacts.get("final_answer")
        analysis_report_path = self.artifacts.get("analysis_report")
        
        if not final_answer_path or not analysis_report_path:
            rprint("Missing required reports for memory writing")
            return 0
            
        # Load report contents
        research_report = load_artifact(final_answer_path)
        analysis_report = load_artifact(analysis_report_path)
        
        # Write memories to mem0
        stored_count = write_memories_from_reports(
            research_report=research_report,
            analysis_report=analysis_report, 
            question=question,
            session_id=self.session_timestamp
        )
        
        return stored_count
    
    def run_complete_pipeline(self, question: str) -> Dict[str, Any]:
        """Run the complete research pipeline"""
        
        rprint("\nStarting Deep Research Pipeline")
        rprint(f"Research Question: {question}")
        
        start_time = time.time()
        
        try:
            # Phase 1: Database Metadata Analysis
            metadata_json = self.phase_1_metadata_analysis()
            
            # Phase 2: Strategic Research Planning  
            research_plan = self.phase_2_strategic_planning(question, metadata_json)
            
            # Phase 3: Strategic Deep Research Execution (using plan + metadata as guidance)
            final_answer, raw_results = self.phase_3_strategic_deep_research(question, research_plan, metadata_json)
            
            execution_time = time.time() - start_time
            
            # Phase 4: Comprehensive Analysis
            analysis_report = self.phase_4_comprehensive_analysis(question, execution_time)
            
            # Phase 5: Optional Memory Writing
            memories_stored = 0
            try:
                # Ask user if they want to store insights as memories
                rprint("\n" + "="*60)
                rprint("Research pipeline complete!")
                store_memories = input("Do you want to store key insights as memories for future research? (y/n): ").strip().lower()
                
                if store_memories in ['y', 'yes']:
                    memories_stored = self.phase_5_memory_writing(question)
                    rprint(f"Stored {memories_stored} research insights as memories")
                else:
                    rprint("Skipping memory storage")
            except Exception as e:
                rprint(f"Memory writing failed: {e}")
            
            # Display final results
            self.display_completion_summary(question, execution_time, final_answer, memories_stored)
            
            return {
                "success": True,
                "execution_time": execution_time,
                "artifacts": self.artifacts,
                "final_answer": final_answer
            }
            
        except Exception as e:
            rprint(f"Pipeline failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "artifacts": self.artifacts
            }
    
    def display_completion_summary(self, question: str, execution_time: float, final_answer: str, memories_stored: int = 0):
        """Display comprehensive completion summary"""
        
        rprint("\nPipeline execution complete")
        
        rprint(f"\nGenerated Artifacts ({len(self.artifacts)} files):")
        rprint("-" * 60)
        for artifact_type, path in self.artifacts.items():
            rprint(f"  • {artifact_type.replace('_', ' ').title()}: {path}")
        
        rprint(f"\nExecution Summary:")
        rprint("-" * 60)
        rprint(f"  • Total Time: {execution_time:.2f} seconds")
        rprint(f"  • Session ID: {self.session_timestamp}")
        rprint(f"  • Question: {question}")
        if memories_stored > 0:
            rprint(f"  • Memories Stored: {memories_stored} insights saved for future research")
        
        rprint(f"\nFinal Research Report Preview:")
        rprint("-" * 60)
        # Show first 200 characters of the final answer
        preview = final_answer[:200] + "..." if len(final_answer) > 200 else final_answer
        rprint(preview)
        rprint(f"\n[Full report available in: {self.artifacts.get('final_answer', 'N/A')}]")
        


def main():
    """Main entry point with simple input prompts"""
    rprint("Deep Memory Research Pipeline")
    rprint("I'll help you research your mem0 memories comprehensively!")
    rprint()
    
    # Get research question from user
    question = input("What would you like to research? ").strip()
    
    if not question:
        rprint("Please provide a research question.")
        return
    
    rprint(f"\nResearch Question: {question}")
    rprint("Starting comprehensive research...")
    
    # Initialize orchestrator with fixed defaults
    orchestrator = DeepResearchOrchestrator(
        user_id="doctor_memory",  # Fixed default
        max_memories=100          # Fixed default
    )
    
    # Run complete pipeline
    result = orchestrator.run_complete_pipeline(question)
    
    if result.get("success"):
        rprint("\nResearch complete! Check the artifacts folder for detailed reports.")
    else:
        rprint(f"\nResearch failed: {result.get('error', 'Unknown error')}")
    
    # Exit with appropriate code
    sys.exit(0 if result.get("success") else 1)


if __name__ == "__main__":
    main()