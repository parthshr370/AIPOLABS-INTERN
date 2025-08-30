import os
import warnings
from dotenv import load_dotenv
from mem0 import MemoryClient
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from camel.agents import ChatAgent
from camel.messages import BaseMessage
from camel.models import ModelFactory
from camel.types import ModelPlatformType, ModelType

# Suppress noisy deprecation warnings from underlying libraries
warnings.filterwarnings("ignore", category=DeprecationWarning)

load_dotenv()

# API keys and configuration
USER_ID = "doctor_memory"  # Using same user_id as your medical data
MEM0_API_KEY = os.getenv("MEM0_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

console = Console()
if not MEM0_API_KEY or not GEMINI_API_KEY:
    console.print("[red]Error: Missing API keys in environment variables[/red]")
    exit(1)

# Initialize memory and model
mem0 = MemoryClient()
model = ModelFactory.create(
    model_platform=ModelPlatformType.GEMINI,
    model_type=ModelType.GEMINI_2_5_PRO,
    api_key=GEMINI_API_KEY,
    model_config_dict={"temperature": 0.2},
)

class SimpleReActAgent:
    def __init__(self):
        self.mem0 = mem0
        self.model = model
        self.console = console
        self.research_context = {}
        
    def reason(self, question, current_findings):
        """REASONING: Analyze what to search for next"""
        
        reasoning_prompt = f"""
        You are a medical research reasoning agent. Analyze the current research state and decide what to do next.

        RESEARCH QUESTION: {question}
        CURRENT FINDINGS: {current_findings}
        
        REASONING TASK:
        1. What specific aspect should we search for next?
        2. Should this be a broad search (cast wide net) or focused search (specific terms)?
        3. What search terms would be most effective?
        4. Are we ready to provide an answer, or need more information?
        
        Respond in this format:
        REASONING: [Your analysis of what we need next]
        ACTION: [SEARCH_BROAD / SEARCH_FOCUSED / GET_ALL / SYNTHESIZE]  
        QUERY: [Specific search terms to use]
        RATIONALE: [Why this search strategy]
        """
        
        reasoning_agent = ChatAgent(
            system_message=BaseMessage.make_assistant_message(
                role_name="MedicalReasoner",
                content="You analyze medical research progress and plan next steps systematically."
            ),
            model=self.model
        )
        
        response = reasoning_agent.step(
            BaseMessage.make_user_message(role_name="User", content=reasoning_prompt)
        )
        
        return self._parse_reasoning_response(response.msg.content)
    
    def act(self, action_plan):
        """ACTING: Execute the planned search action"""
        
        action_type = action_plan.get('action', 'SEARCH_BROAD')
        query = action_plan.get('query', '')
        
        console.print(f"[yellow]🔍 ACTION: {action_type} - Searching: '{query}'[/yellow]")
        
        if action_type == 'SEARCH_BROAD':
            # Broad search: lower threshold, higher limit
            memories = self.mem0.search(
                query=query,
                user_id=USER_ID,
                limit=20,
                threshold=0.3
            )
        elif action_type == 'SEARCH_FOCUSED':
            # Focused search: higher threshold, lower limit
            memories = self.mem0.search(
                query=query,
                user_id=USER_ID, 
                limit=10,
                threshold=0.6
            )
        elif action_type == 'GET_ALL':
            # Get all memories matching specific criteria
            memories = self.mem0.get_all(
                user_id=USER_ID,
                limit=50
            )
        else:
            memories = []
            
        return memories
    
    def observe(self, search_results, original_question):
        """OBSERVING: Analyze search results and extract insights"""
        
        if not search_results:
            return {
                'insights': 'No relevant memories found for this search.',
                'continue_research': True
            }
        
        observation_prompt = f"""
        You are a medical research observer. Analyze these search results for patterns and insights.

        ORIGINAL QUESTION: {original_question}
        SEARCH RESULTS: {search_results}
        
        OBSERVATION TASK:
        1. What key medical insights can you extract from these memories?
        2. What patterns do you see across different patients or cases?
        3. Are there any trends in treatment effectiveness or outcomes?
        4. What gaps still exist in answering the original question?
        5. Should we continue researching or do we have enough information?
        
        Respond in this format:
        INSIGHTS: [Key findings from this search]
        PATTERNS: [Any patterns you notice]
        GAPS: [What information is still missing]
        CONTINUE: [YES/NO - whether to continue research]
        """
        
        observer_agent = ChatAgent(
            system_message=BaseMessage.make_assistant_message(
                role_name="MedicalObserver",
                content="You extract medical insights and identify research gaps from memory search results."
            ),
            model=self.model
        )
        
        response = observer_agent.step(
            BaseMessage.make_user_message(role_name="User", content=observation_prompt)
        )
        
        return self._parse_observation_response(response.msg.content, search_results)
    
    def deep_research(self, question):
        """Main ReAct loop: Reason -> Act -> Observe -> Repeat"""
        
        console.print(Panel(
            f"[bold blue]🧠 Starting Deep Medical Research[/bold blue]\n\n"
            f"Research Question: {question}\n\n"
            f"Using ReAct methodology: Reasoning → Acting → Observing",
            title="🔬 Medical Research Agent",
            border_style="cyan"
        ))
        
        all_findings = {}
        step = 1
        max_steps = 5
        
        while step <= max_steps:
            console.print(f"\n[bold magenta]═══ STEP {step} ═══[/bold magenta]")
            
            # REASON: What should we search for?
            console.print("[cyan]💭 REASONING: Analyzing research gaps...[/cyan]")
            reasoning_result = self.reason(question, all_findings)
            console.print(f"[green]✓ Reasoning: {reasoning_result.get('rationale', 'Planning next search')}[/green]")
            
            # Check if we should synthesize instead of search more
            if reasoning_result.get('action') == 'SYNTHESIZE':
                console.print("[yellow]🎯 Ready to synthesize findings![/yellow]")
                break
            
            # ACT: Execute the search
            search_results = self.act(reasoning_result)
            
            # OBSERVE: Analyze what we found
            console.print("[cyan]👁️ OBSERVING: Analyzing search results...[/cyan]")
            observation = self.observe(search_results, question)
            
            # Display findings for this step
            self._display_step_results(step, reasoning_result, observation)
            
            # Store findings
            all_findings[f"step_{step}"] = {
                'reasoning': reasoning_result,
                'search_results': search_results,
                'observation': observation
            }
            
            # Check if we should continue
            if not observation.get('continue_research', True):
                console.print("[green]✅ Research complete - sufficient information gathered![/green]")
                break
                
            step += 1
        
        # SYNTHESIZE: Create final comprehensive answer
        return self._synthesize_final_answer(question, all_findings)
    
    def _parse_reasoning_response(self, response):
        """Parse the reasoning agent's response"""
        lines = response.split('\n')
        result = {}
        
        for line in lines:
            if line.startswith('ACTION:'):
                result['action'] = line.replace('ACTION:', '').strip()
            elif line.startswith('QUERY:'):
                result['query'] = line.replace('QUERY:', '').strip()
            elif line.startswith('RATIONALE:'):
                result['rationale'] = line.replace('RATIONALE:', '').strip()
        
        # Defaults
        result.setdefault('action', 'SEARCH_BROAD')
        result.setdefault('query', 'medical treatment')
        result.setdefault('rationale', 'General medical search')
        
        return result
    
    def _parse_observation_response(self, response, raw_results):
        """Parse the observation agent's response"""
        lines = response.split('\n')
        result = {'raw_results': raw_results}
        
        for line in lines:
            if line.startswith('INSIGHTS:'):
                result['insights'] = line.replace('INSIGHTS:', '').strip()
            elif line.startswith('PATTERNS:'):
                result['patterns'] = line.replace('PATTERNS:', '').strip()
            elif line.startswith('GAPS:'):
                result['gaps'] = line.replace('GAPS:', '').strip()
            elif line.startswith('CONTINUE:'):
                continue_text = line.replace('CONTINUE:', '').strip().upper()
                result['continue_research'] = 'YES' in continue_text
        
        # Defaults
        result.setdefault('insights', 'Processing search results...')
        result.setdefault('continue_research', True)
        
        return result
    
    def _display_step_results(self, step, reasoning, observation):
        """Display results for each research step"""
        
        table = Table(title=f"Step {step} Results")
        table.add_column("Component", style="cyan")
        table.add_column("Finding", style="white")
        
        table.add_row("🧠 Reasoning", reasoning.get('rationale', 'N/A'))
        table.add_row("🎯 Action", reasoning.get('action', 'N/A'))
        table.add_row("🔍 Query", reasoning.get('query', 'N/A'))
        table.add_row("💡 Key Insights", observation.get('insights', 'N/A'))
        table.add_row("🔄 Continue?", "Yes" if observation.get('continue_research') else "No")
        
        console.print(table)
    
    def _synthesize_final_answer(self, question, all_findings):
        """Create comprehensive final answer from all research steps"""
        
        synthesis_prompt = f"""
        You are a medical research synthesizer. Create a comprehensive, evidence-based answer to the research question.

        RESEARCH QUESTION: {question}
        ALL RESEARCH FINDINGS: {all_findings}
        
        SYNTHESIS TASK:
        Create a detailed medical research report that includes:
        
        1. **EXECUTIVE SUMMARY**: Brief answer to the main question
        2. **KEY FINDINGS**: Most important discoveries from your research
        3. **EVIDENCE**: Specific examples from the medical memories
        4. **PATTERNS IDENTIFIED**: Recurring themes across different searches  
        5. **CLINICAL INSIGHTS**: Practical medical implications
        6. **RECOMMENDATIONS**: Actionable suggestions based on findings
        
        Format your response clearly with headers and bullet points for easy reading.
        """
        
        synthesizer_agent = ChatAgent(
            system_message=BaseMessage.make_assistant_message(
                role_name="MedicalSynthesizer",
                content="You create comprehensive medical research reports from research findings."
            ),
            model=self.model
        )
        
        response = synthesizer_agent.step(
            BaseMessage.make_user_message(role_name="User", content=synthesis_prompt)
        )
        
        return response.msg.content

def main():
    """Simple ReAct Medical Research Agent Interface"""
    
    console.print(Panel(
        "[bold blue]🧠 Simple ReAct Medical Research Agent[/bold blue]\n\n"
        "Ask me complex medical research questions and I'll use ReAct methodology to find answers.\n\n"
        "💡 [bold]Example questions:[/bold]\n"
        "• 'What are my most effective pain management approaches?'\n"
        "• 'How do my diabetes treatments compare in effectiveness?'\n"
        "• 'What patterns exist in my chronic disease management?'\n\n"
        "Type 'exit' to quit.",
        title="🔬 Deep Medical Research System",
        border_style="green"
    ))
    
    agent = SimpleReActAgent()
    
    while True:
        try:
            user_input = console.input("\n[bold cyan]Medical Research Question:[/bold cyan] ").strip()
            
            if user_input.lower() in ['exit', 'quit']:
                console.print("[yellow]Research session ended. Goodbye![/yellow]")
                break
                
            if not user_input:
                continue
            
            # Start deep research using ReAct methodology
            final_answer = agent.deep_research(user_input)
            
            # Display final comprehensive answer
            console.print(Panel(
                final_answer,
                title="🎯 Research Synthesis - Final Answer",
                border_style="green"
            ))
            
        except KeyboardInterrupt:
            console.print("\n[yellow]Research interrupted. Goodbye![/yellow]")
            break
        except Exception as e:
            console.print(f"[red]Error during research: {e}[/red]")

if __name__ == "__main__":
    main()