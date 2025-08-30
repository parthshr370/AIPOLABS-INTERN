"""
Memory Writer - Converts research reports into actionable memories for mem0 storage
Simple module that extracts key insights and stores them as structured memories
"""

import os
import json
from dotenv import load_dotenv
from mem0.client.main import MemoryClient
from rich import print as rprint

from camel.agents import ChatAgent
from camel.messages import BaseMessage
from camel.models import ModelFactory
from camel.types import ModelPlatformType, ModelType

# Load environment variables
load_dotenv()

# Configuration
USER_ID = "deep_researcher"
MEM0_API_KEY = os.getenv("MEM0_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not MEM0_API_KEY or not GEMINI_API_KEY:
    raise ValueError("Missing required API keys: MEM0_API_KEY and GEMINI_API_KEY")


class MemoryWriter:
    def __init__(self):
        self.mem0 = MemoryClient(api_key=MEM0_API_KEY)
        
        # Simple model for memory extraction
        self.model = ModelFactory.create(
            model_platform=ModelPlatformType.GEMINI,
            model_type=ModelType.GEMINI_2_5_FLASH,
            api_key=GEMINI_API_KEY,
            model_config_dict={"temperature": 0.1},
        )
    
    def extract_actionable_memories(self, research_report: str, analysis_report: str, question: str) -> list:
        """Extract actionable memories from research and analysis reports"""
        
        prompt = f"""RESEARCH QUESTION: {question}

RESEARCH REPORT:
{research_report}

ANALYSIS REPORT:
{analysis_report}

Extract 8 small, specific insights and return them in this EXACT JSON format:

[
  {{"memory": "Database contains no explicit ethnicity data for patients", "topic": "data_gaps"}},
  {{"memory": "Kaelen Vance appears in 28 memory entries indicating complex case", "topic": "patient_patterns"}},
  {{"memory": "Memory network focuses on challenging clinical cases not routine care", "topic": "selection_bias"}},
  {{"memory": "Research premise was invalid due to missing demographic data", "topic": "methodology"}},
  {{"memory": "Future research should validate data existence before planning", "topic": "process_improvement"}},
  {{"memory": "Patient names suggest diverse backgrounds but no explicit ethnicity recorded", "topic": "data_inference"}},
  {{"memory": "Analysis revealed catalog of end-stage disease management", "topic": "clinical_focus"}},
  {{"memory": "Total execution time was 142 seconds for this research session", "topic": "performance"}}
]

Return ONLY the JSON array with 8 entries like above. No other text."""

        system_message = BaseMessage.make_assistant_message(
            role_name="MemoryExtractor",
            content="You extract research insights into exactly 8 JSON memory objects. Return only the JSON array, nothing else."
        )
        
        agent = ChatAgent(system_message=system_message, model=self.model)
        response = agent.step(BaseMessage.make_user_message("User", prompt))
        
        try:
            memory_data = json.loads(response.msg.content.strip())
            return memory_data
        except json.JSONDecodeError as e:
            rprint(f"Memory extraction failed: {e}")
            return []
    
    def store_memories(self, memories: list, session_id: str, question: str) -> int:
        """Store extracted memories in mem0 - simple loop"""
        
        stored_count = 0
        
        for i, memory_entry in enumerate(memories):
            memory_text = memory_entry.get("memory", "")
            topic = memory_entry.get("topic", "research")
            
            if memory_text:
                try:
                    self.mem0.add(
                        messages=[{"role": "assistant", "content": memory_text}],
                        user_id=USER_ID,
                        metadata={
                            "session_id": session_id,
                            "research_question": question,
                            "topic": topic,
                            "memory_type": "research_insight"
                        }
                    )
                    stored_count += 1
                    rprint(f"   ✓ {i+1}. {memory_text}")
                except:
                    rprint(f"   ✗ Failed to store memory {i+1}")
        
        return stored_count
    
    def process_research_session(self, research_report: str, analysis_report: str, question: str, session_id: str) -> int:
        """Main function to process a research session and store memories"""
        
        # Extract memories from reports
        memories = self.extract_actionable_memories(research_report, analysis_report, question)
        
        if not memories:
            rprint("No memories extracted")
            return 0
        
        # Store memories - simple loop
        rprint(f"Storing {len(memories)} memories:")
        stored_count = self.store_memories(memories, session_id, question)
        
        return stored_count


def write_memories_from_reports(research_report: str, analysis_report: str, question: str, session_id: str) -> int:
    """Convenience function to write memories from research reports"""
    
    writer = MemoryWriter()
    return writer.process_research_session(research_report, analysis_report, question, session_id)


if __name__ == "__main__":
    # Test the memory writer
    test_report = "Test research findings about diabetes treatment patterns in elderly patients..."
    test_analysis = "Analysis shows high-quality methodology with good data coverage..."
    test_question = "What are the most effective diabetes treatments for elderly patients?"
    test_session = "20241213_test"
    
    count = write_memories_from_reports(test_report, test_analysis, test_question, test_session)
    print(f"Stored {count} test memories")