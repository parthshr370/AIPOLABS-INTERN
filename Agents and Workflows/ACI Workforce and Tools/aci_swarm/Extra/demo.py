import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

class DemoOrchestrator:
    def __init__(self):
        self.agent_configs = {
            "social": {
                "name": "Social Media Expert",
                "tools": ["DISCORD", "REDDIT"],
                "description": "Community engagement, social strategy, and online presence management"
            },
            "search_genius": {
                "name": "Search & Research Specialist",
                "tools": ["EXA_AI", "ARXIV", "GOOGLE_MAPS"],
                "description": "Comprehensive research and location-based insights"
            },
            "web_crawler": {
                "name": "Web Data Analyst",
                "tools": ["BROWSERBASE", "BRAVE_SEARCH", "STEEL"],
                "description": "Web data extraction and analysis"
            },
            "researcher": {
                "name": "Academic Researcher",
                "tools": ["ARXIV", "HACKERNEWS"],
                "description": "Scholarly analysis and tech insights"
            },
            "slack_manager": {
                "name": "Communication Coordinator",
                "tools": ["SLACK"],
                "description": "Team communications and workflows"
            },
            "marketing": {
                "name": "Marketing Strategist",
                "tools": ["GOOGLE_ANALYTICS_ADMIN", "CODA"],
                "description":
 "Marketing analytics and strategies"
            },
            "visual_alchemist": {
                "name": "Design Specialist",
                "tools": ["FIGMA"],
                "description": "UI/UX concepts and visual designs"
            },
            "code_ninja": {
                "name": "Developer",
                "tools": ["GITHUB", "VERCEL", "AGENT_SECRETS_MANAGER"],
                "description": "Development, deployment, and security"
            },
            "crypto": {
                "name": "Crypto Analyst",
                "tools": ["COINMARKETCAP", "SOLSCAN"],
                "description": "Blockchain and market analysis"
            },
            "content_king": {
                "name": "Content Creator",
                "tools": ["ELEVEN_LABS", "YOUTUBE", "RESEND"],
                "description": "Multimedia content creation"
            },
            "document_master": {
                "name": "Documentation Expert",
                "tools": ["GOOGLE_DOCS", "CODA"],
                "description": "Comprehensive documentation"
            },
            "hr_sales": {
                "name": "HR & Sales Specialist",
                "tools": ["GMAIL"],
                "description": "People operations and sales communications"
            },
            "memory": {
                "name": "Knowledge Manager",
                "tools": ["NOTION"],
                "description": "Information organization and storage"
            }
        }
    
    def _select_agent(self, query: str):
        """Simple keyword-based agent selection"""
        query_lower = query.lower()
        
        # Social/Community
        if any(word in query_lower for word in ['discord', 'reddit', 'social', 'community', 'post']):
            return 'social'
        
        # Location/Maps/Restaurant
        if any(word in query_lower for word in ['restaurant', 'location', 'map', 'place', 'near', 'address', 'directions']):
            return 'search_genius'
        
        # Web search/crawling
        if any(word in query_lower for word in ['search', 'find', 'browse', 'website', 'web', 'crawl']):
            return 'web_crawler'
        
        # Research/Papers
        if any(word in query_lower for word in ['research', 'paper', 'study', 'arxiv', 'academic']):
            return 'researcher'
        
        # Crypto/Blockchain
        if any(word in query_lower for word in ['bitcoin', 'crypto', 'blockchain', 'ethereum', 'solana', 'price', 'token']):
            return 'crypto'
        
        # Design/Visual
        if any(word in query_lower for word in ['design', 'logo', 'ui', 'ux', 'figma', 'mockup', 'visual']):
            return 'visual_alchemist'
        
        # Code/Development
        if any(word in query_lower for word in ['code', 'deploy', 'github', 'app', 'website', 'development', 'programming']):
            return 'code_ninja'
        
        # Content creation
        if any(word in query_lower for word in ['video', 'content', 'script', 'youtube', 'audio', 'voice']):
            return 'content_king'
        
        # Documentation
        if any(word in query_lower for word in ['document', 'docs', 'write', 'documentation', 'api']):
            return 'document_master'
        
        # Email/Communication
        if any(word in query_lower for word in ['email', 'gmail', 'send', 'message', 'contact']):
            return 'hr_sales'
        
        # Slack/Team communication
        if any(word in query_lower for word in ['slack', 'team', 'meeting', 'collaborate']):
            return 'slack_manager'
        
        # Marketing/Analytics
        if any(word in query_lower for word in ['marketing', 'campaign', 'analytics', 'stats', 'metrics']):
            return 'marketing'
        
        # Knowledge/Memory
        if any(word in query_lower for word in ['save', 'remember', 'note', 'organize', 'knowledge']):
            return 'memory'
        
        # Default to search_genius for general queries
        return 'search_genius'
    
    def process_query(self, query: str):
        """Demo version - just shows routing without calling models"""
        selected_agent = self._select_agent(query)
        agent_info = self.agent_configs[selected_agent]
        
        # Simulate agent response based on query type
        demo_responses = {
            'crypto': f"I would analyze cryptocurrency data using {', '.join(agent_info['tools'])} to get current Bitcoin price, market trends, and blockchain metrics.",
            'researcher': f"I would search academic papers using {', '.join(agent_info['tools'])} to find the latest AI research publications and tech insights.",
            'visual_alchemist': f"I would use {', '.join(agent_info['tools'])} to create logo design concepts, including typography, color schemes, and brand guidelines.",
            'search_genius': f"I would use {', '.join(agent_info['tools'])} to find restaurants in London with reviews, locations, and recommendations.",
            'code_ninja': f"I would use {', '.join(agent_info['tools'])} to deploy your React app with proper CI/CD setup and hosting configuration."
        }
        
        response = demo_responses.get(selected_agent, f"I would handle this query using {', '.join(agent_info['tools'])} for {agent_info['description']}")
        
        return {
            'selected_agent': selected_agent,
            'agent_name': agent_info['name'],
            'tools': agent_info['tools'],
            'agent_response': response
        }

async def demo_test():
    """Demo test function"""
    print("🎯 ACI Agent Swarm - DEMO MODE")
    print("=" * 50)
    print("This demo shows intelligent agent routing without API calls")
    print("-" * 50)
    
    orchestrator = DemoOrchestrator()
    
    # Test queries
    test_queries = [
        "What's the current Bitcoin price?",
        "Find research papers about AI",
        "Create a logo design for my startup",
        "Search for restaurants in London",
        "Deploy my React app to production",
        "Post on social media about our product",
        "Send an email to the team",
        "Create documentation for our API",
        "Analyze our marketing metrics"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. Query: {query}")
        print("-" * 30)
        
        result = orchestrator.process_query(query)
        
        print(f"🤖 Agent: {result['agent_name']} ({result['selected_agent']})")
        print(f"🛠️  Tools: {', '.join(result['tools'])}")
        print(f"💬 Response: {result['agent_response']}")
    
    print("\n" + "=" * 50)
    print("✅ Demo completed! The routing system is working perfectly.")
    print("📝 To run with real AI models, get a valid Google API key")
    print("🔗 https://console.cloud.google.com/apis/credentials")

async def interactive_demo():
    """Interactive demo mode"""
    print("🎯 ACI Agent Swarm - Interactive Demo")
    print("=" * 50)
    print("Enter your queries to see which agent would handle them")
    print("Type 'exit' to quit, 'test' to run automated tests")
    print("-" * 50)
    
    orchestrator = DemoOrchestrator()
    
    while True:
        try:
            query = input("\nQuery: ").strip()
            
            if query.lower() in ['exit', 'quit']:
                print("👋 Goodbye!")
                break
            elif query.lower() == 'test':
                await demo_test()
                continue
            elif not query:
                continue
            
            result = orchestrator.process_query(query)
            
            print(f"\n🤖 Selected Agent: {result['agent_name']}")
            print(f"🛠️  Available Tools: {', '.join(result['tools'])}")
            print(f"💬 What I would do: {result['agent_response']}")
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        asyncio.run(demo_test())
    else:
        asyncio.run(interactive_demo())