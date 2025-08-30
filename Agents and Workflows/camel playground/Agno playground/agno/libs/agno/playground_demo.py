from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.playground import Playground, serve_playground_app
from agno.storage.sqlite import SqliteStorage
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.yfinance import YFinanceTools

# Storage for agent sessions
agent_storage = "tmp/agents.db"

# Create a web search agent
web_agent = Agent(
    name="Web Search Agent",
    model=OpenAIChat(id="gpt-4o-mini"),  # Using mini for cost efficiency
    tools=[DuckDuckGoTools()],
    instructions=["Always include sources", "Be concise but informative"],
    storage=SqliteStorage(table_name="web_agent", db_file=agent_storage),
    add_datetime_to_instructions=True,
    add_history_to_messages=True,
    num_history_responses=5,
    markdown=True,
)

# Create a finance agent
finance_agent = Agent(
    name="Finance Agent", 
    model=OpenAIChat(id="gpt-4o-mini"),
    tools=[YFinanceTools(stock_price=True, analyst_recommendations=True, company_info=True, company_news=True)],
    instructions=["Always use tables to display data", "Provide clear financial analysis"],
    storage=SqliteStorage(table_name="finance_agent", db_file=agent_storage),
    add_datetime_to_instructions=True,
    add_history_to_messages=True,
    num_history_responses=5,
    markdown=True,
)

# Create the playground
playground = Playground(
    agents=[web_agent, finance_agent],
    name="Demo Playground",
    description="A simple playground with web search and finance agents"
)

# Get the FastAPI app
app = playground.get_app()

if __name__ == "__main__":
    # Serve the playground
    serve_playground_app("playground_demo:app", reload=True) 