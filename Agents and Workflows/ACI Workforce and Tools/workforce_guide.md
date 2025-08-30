CAMEL-AI Workforce: The Ultimate Guide
Table of Contents

Introduction to Workforce
System Design and Architecture
Communication Model
Failure Handling
Quickstart Guide
Use Cases
Key Functions and Classes
Configuration and Setup
Advanced Features
Complete Running Example

1. Introduction to Workforce
   Workforce is a multi-agent teamwork engine in CAMEL-AI that enables a group of specialized agents to collaborate under a single, coordinated system. It is designed to handle complex tasks by leveraging planning, parallelization, and diverse expertise among agents. Whether you're scaling from a single agent to a team or tackling workflows that require multiple perspectives, Workforce provides a robust framework for task management and execution.
   Key Benefits

Scalability: Seamlessly scale from one agent to many.
Coordination: Built-in task planning and assignment.
Resilience: Handles failures with retry and escalation mechanisms.
Flexibility: Applicable to a wide range of scenarios, from evaluations to brainstorming.

2. System Design and Architecture
   Workforce uses a hierarchical, modular architecture to manage multi-agent collaboration:

Workforce: The top-level entity that orchestrates the team.
Coordinator Agent: The "project manager" that routes tasks to worker nodes based on their roles.
Task Planner Agent: The "strategist" that decomposes tasks into subtasks and defines the workflow.
Worker Nodes: Individual agents or groups of agents with specific skills.

Simplified Architecture Diagram
+-------------------+ +-------------------+
| Task Planner |<------->| Coordinator |
| (Decomposes | | (Assigns tasks) |
| tasks) | | |
+-------------------+ +-------------------+
| |
v v
+-------------------+ +-------------------+
| Worker Node 1 | | Worker Node 2 |
| (Agent A) | | (Agent B) |
+-------------------+ +-------------------+
| |
v v
+-------------------+ +-------------------+
| Shared Task |<------->| Shared Task |
| Channel | | Channel |
+-------------------+ +-------------------+

3. Communication Model
   Workforce employs a shared task channel for agent communication:

Tasks are posted to the channel by the coordinator or planner.
Worker nodes listen to the channel and pick up tasks assigned to them.
Results are posted back to the channel, enabling downstream tasks to use them as dependencies.

This model ensures transparency and continuity across the workflow.

4. Failure Handling
   Workforce is built to recover from failures efficiently:

Task Retry: If a worker fails, the coordinator can decompose the task into smaller parts and retry.
Escalation: A new worker can be created to handle a specific failure.
Loop Prevention: Workflows halt if a task fails or is decomposed beyond a threshold (default: 3 attempts).

This resilience makes Workforce reliable for critical applications.

5. Quickstart Guide
   Here’s how to get started with Workforce:
   Step 1: Install CAMEL-AI
   pip install "camel-ai[all]==0.2.4"

Step 2: Create a Workforce Instance
from camel.societies.workforce import Workforce

workforce = Workforce("My Team")

Step 3: Add Worker Nodes
Define agents with specific roles and add them to the workforce.
from camel.agents import ChatAgent
from camel.messages import BaseMessage
from camel.models import ModelFactory
from camel.types import ModelPlatformType, ModelType

# Create an agent

agent = ChatAgent(
system_message=BaseMessage.make_assistant_message(
role_name="Worker",
content="I am a worker agent specializing in data analysis."
),
model=ModelFactory.create(model_platform=ModelPlatformType.OPENAI, model_type=ModelType.GPT_4O)
)

# Add to workforce

workforce.add_single_agent_worker("Data Analyst Agent", worker=agent)

Step 4: Define and Process a Task
from camel.tasks import Task

task = Task(content="Analyze this dataset: [1, 2, 3, 4, 5]", id="1")
result = workforce.process_task(task)
print(result.result)

6. Use Cases
   Workforce shines in scenarios requiring collaboration and diverse expertise. Here are some examples:
   Hackathon Judging
   Multiple judge agents evaluate projects based on unique criteria (e.g., scalability, innovation).
   Code Review
   Agents with different technical expertise (e.g., Python, security) review code collaboratively.
   Brainstorming
   Creative agents generate and refine ideas together.
   Data Analysis
   Specialized agents process and interpret data in parallel.
   Customer Support Simulation
   Agents with different personas respond to mock customer queries.

7. Key Functions and Classes
   Workforce Class

Workforce(description): Initializes a workforce with a descriptive name.workforce = Workforce("Code Review Team")

add_single_agent_worker(description, worker): Adds an agent as a worker node.workforce.add_single_agent_worker("Python Expert", worker=python_agent)

process_task(task): Processes a task and returns the result.result = workforce.process_task(task)

Task Class

Task(content, additional_info=None, id="0"): Creates a task.task = Task(content="Review this code", additional_info="Code: def foo(): pass")

ChatAgent Class

ChatAgent(system_message, model, tools=None): Creates an agent with a system message, model, and optional tools.agent = ChatAgent(
system_message=BaseMessage.make_assistant_message(role_name="Coder", content="I write code."),
model=ModelFactory.create(model_platform=ModelPlatformType.OPENAI, model_type=ModelType.GPT_4O)
)

Tools and Toolkits

SearchToolkit(): Provides search tools (e.g., Google, DuckDuckGo).from camel.toolkits import SearchToolkit
toolkit = SearchToolkit()
tools = [FunctionTool(toolkit.search_google)]
agent = ChatAgent(..., tools=tools)

8. Configuration and Setup
   API Keys
   Set environment variables for required APIs:
   import os
   os.environ["OPENAI_API_KEY"] = "your_openai_key"
   os.environ["GOOGLE_API_KEY"] = "your_google_key" # For search tools
   os.environ["SEARCH_ENGINE_ID"] = "your_search_engine_id"

Asynchronous Handling
Workforce uses coroutines. In Jupyter or similar environments:
import nest_asyncio
nest_asyncio.apply()

9. Advanced Features
   Custom Coordinator and Planner
   Override default agents:
   custom_coordinator = ChatAgent(...) # Define your coordinator
   workforce = Workforce("Custom Team", coordinator_agent=custom_coordinator)

Complex Workflows
Use additional_info in tasks to pass context:
task = Task(content="Solve this problem", additional_info="Details: X, Y, Z")

Tool Integration
Equip agents with tools for enhanced functionality:
from camel.toolkits import FunctionTool
agent = ChatAgent(..., tools=[FunctionTool(my_custom_function)])

10. Complete Running Example
    This example implements a Hackathon Judging Committee with multiple judge agents and a researcher.
    Full Code
    import os
    from getpass import getpass
    import nest_asyncio
    from camel.agents import ChatAgent
    from camel.messages import BaseMessage
    from camel.models import ModelFactory
    from camel.societies.workforce import Workforce
    from camel.tasks import Task
    from camel.toolkits import FunctionTool, SearchToolkit
    from camel.types import ModelPlatformType, ModelType

# Set API keys

os.environ["OPENAI_API_KEY"] = getpass("Enter your OpenAI API key: ")
os.environ["GOOGLE_API_KEY"] = getpass("Enter your Google API key: ")
os.environ["SEARCH_ENGINE_ID"] = getpass("Enter your Search Engine ID: ")

# Enable nested event loops

nest_asyncio.apply()

# Helper function to create judge agents

def make_judge(persona, example_feedback, criteria):
content = f"""You are a hackathon judge with persona: {persona}.
Example feedback: {example_feedback}.
Criteria: {criteria}.
Score from 1-4 (e.g., 3/4)."""
sys_msg = BaseMessage.make_assistant_message(role_name="Judge", content=content)
model = ModelFactory.create(model_platform=ModelPlatformType.OPENAI, model_type=ModelType.GPT_4O)
return ChatAgent(system_message=sys_msg, model=model)

# Create agents

researcher = ChatAgent(
system_message=BaseMessage.make_assistant_message(
role_name="Researcher",
content="I research AI trends using web search."
),
model=ModelFactory.create(model_platform=ModelPlatformType.OPENAI, model_type=ModelType.GPT_4O),
tools=[FunctionTool(SearchToolkit().search_google)]
)

judge1 = make_judge(
"Venture capitalist focused on scalability",
"This has unicorn potential but needs more market reach.",
"Scalability"
)
judge2 = make_judge(
"Engineer obsessed with technical perfection",
"Solid code, but edge cases are unhandled.",
"Technical Quality"
)

# Create workforce

workforce = Workforce("Hackathon Judges")
workforce.add_single_agent_worker("Researcher Rachel", worker=researcher)
workforce.add_single_agent_worker("Judge Veronica", worker=judge1)
workforce.add_single_agent_worker("Judge John", worker=judge2)

# Define task

task = Task(
content="Evaluate this project: AI-Powered Chatbot",
additional_info="Details: Uses GPT-4o, deployed on cloud.",
id="0"
)

# Process task

result = workforce.process_task(task)
print("Result:", result.result)

Expected Output
The output will include research findings and scores from each judge, e.g.:
Result: Researcher Rachel: "Found trends in AI chatbots..."
Judge Veronica: "Scalability: 3/4 - Great potential, needs broader reach."
Judge John: "Technical Quality: 2/4 - Solid but lacks edge case handling."

This guide provides everything you need to master Workforce in CAMEL-AI. Experiment with the examples and adapt them to your use cases!
