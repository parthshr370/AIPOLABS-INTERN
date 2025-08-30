import asyncio
import os
from dotenv import load_dotenv
from agents import AgentManager, AGENTS

load_dotenv()

class SimpleOrchestrator:
    def __init__(self):
        self.agent_manager = AgentManager()
    
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
    
    async def process_query(self, query: str):
        """Process a query by routing to the appropriate agent"""
        selected_agent = self._select_agent(query)
        agent_info = AGENTS.get(selected_agent, {})
        
        print(f"Routing to: {agent_info.get('name', selected_agent)}")
        
        try:
            response = await self.agent_manager.run_agent(selected_agent, query)
            
            # Simple fallback if tool unavailable
            if "tool is currently unavailable" in response.lower() or "cannot fulfill this request" in response.lower():
                fallback_agent = 'web_crawler' if selected_agent != 'web_crawler' else 'researcher'
                print(f"Tool unavailable, trying: {fallback_agent}")
                response = await self.agent_manager.run_agent(fallback_agent, query)
                response = f"(Used {fallback_agent} as fallback)\n\n{response}"
            
            return {
                'selected_agent': selected_agent,
                'agent_response': response
            }
        except Exception as e:
            return {
                'selected_agent': selected_agent,
                'agent_response': f"Error: {str(e)}"
            }
    
    async def cleanup(self):
        """Cleanup resources"""
        await self.agent_manager.cleanup()