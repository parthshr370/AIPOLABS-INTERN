#!/usr/bin/env python3
"""
🧠 Comprehensive Mem0 + CAMEL AI Agent Demo
===============================================

This demo showcases the complete functionality of the enhanced Mem0CloudToolkit
with CAMEL AI, demonstrating all 18+ memory management features including:

- Core memory operations (add, get, update, delete)
- Advanced search with semantic matching and filters
- Batch operations for efficiency
- Entity management and history tracking
- Export and analytics capabilities
- Memory feedback and quality control
- Interactive conversational agent with persistent memory

Features Demonstrated:
- Personal Assistant Agent with memory
- Multi-session conversation continuity
- Advanced memory search patterns
- Batch memory operations
- Memory analytics and insights
- Real-time memory feedback
- Export functionality
- Entity management
"""

import os
import json
import time
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt, Confirm
from rich.markdown import Markdown

# CAMEL AI imports
from camel.agents import ChatAgent
from camel.messages import BaseMessage
from camel.models import ModelFactory
from camel.types import ModelPlatformType, ModelType

# Import our enhanced toolkit
from mem_camel_toolkit import Mem0CloudToolkit

console = Console()

class ComprehensiveMemoryAgent:
    """
    A sophisticated AI agent that demonstrates all features of the Mem0CloudToolkit.
    This agent can handle complex memory operations, maintain conversation context,
    and provide advanced memory analytics.
    """
    
    def __init__(self, agent_id: str = "comprehensive-agent", user_id: str = "demo-user"):
        self.agent_id = agent_id
        self.user_id = user_id
        self.console = Console()
        
        # Initialize the enhanced toolkit with all features
        self.toolkit = Mem0CloudToolkit(
            agent_id=self.agent_id, 
            user_id=self.user_id,
            timeout=30.0  # 30 second timeout for operations
        )
        
        # Get all available tools (18+ tools)
        self.tools = self.toolkit.get_tools()
        
        # Initialize the language model
        self.model = ModelFactory.create(
            model_platform=ModelPlatformType.OPENAI,
            model_type=ModelType.GPT_4O_MINI,
        )
        
        # Create sophisticated system message
        self.system_message = self._create_system_message()
        
        # Create the agent with all memory tools
        sys_msg = BaseMessage.make_assistant_message(
            role_name="Mem0 Memory Master",
            content=self.system_message,
        )
        
        self.agent = ChatAgent(sys_msg, model=self.model, tools=self.tools)
        
        # Track conversation for analytics
        self.conversation_history = []
        self.memory_operations = []
        
    def _create_system_message(self) -> str:
        """Create a comprehensive system message that explains all capabilities."""
        return """
You are Mem0 Memory Master, an advanced AI agent with comprehensive memory management capabilities.

You have access to 18+ powerful memory tools:

🎯 CORE OPERATIONS:
- add_memory: Store new information with metadata and advanced options
- get_memory: Retrieve specific memories by ID
- retrieve_memories: Get all memories with filtering and pagination
- search_memories: Advanced semantic search with filters, thresholds, reranking
- update_memory: Modify existing memories with new content or metadata
- delete_memory: Remove specific memories by ID
- delete_memories: Bulk delete with filtering options

📊 ADVANCED FEATURES:
- get_memory_history: Track changes and evolution of memories
- get_users: List all entities (users, agents, sessions) with memories
- delete_users: Clean up entity data
- reset_memory: Complete system reset
- batch_update_memories: Efficient bulk updates
- batch_delete_memories: Efficient bulk deletions
- provide_feedback: Quality control and improvement
- create_memory_export: Structured data export
- get_memory_export: Retrieve exported data
- get_memory_summary: Analytics and insights

🧠 INTELLIGENT BEHAVIOR:
1. Always explain what memory operation you're performing
2. Use advanced search features like filters, thresholds, and reranking
3. Provide insights from memory analytics
4. Suggest related memories and connections
5. Handle errors gracefully and explain issues
6. Use metadata effectively for organization
7. Demonstrate batch operations when appropriate
8. Provide memory feedback to improve quality

🎨 CONVERSATION STYLE:
- Be conversational and helpful
- Explain memory operations clearly
- Show enthusiasm about memory capabilities
- Provide detailed results when requested
- Ask clarifying questions when needed
- Suggest memory optimization strategies
"""

    def start_comprehensive_demo(self):
        """Start the comprehensive demonstration of all features."""
        self.console.print(Panel.fit(
            "[bold blue]🧠 Mem0 + CAMEL AI Comprehensive Demo[/bold blue]\n"
            "[dim]Enhanced Toolkit with 18+ Memory Management Tools[/dim]",
            border_style="blue"
        ))
        
        # Show available tools
        self._display_available_tools()
        
        # Run demo modes
        while True:
            self.console.print("\n[bold cyan]Choose a demo mode:[/bold cyan]")
            self.console.print("1. 💬 Interactive Chat (Full conversational experience)")
            self.console.print("2. 🎯 Feature Showcase (Systematic tool demonstration)")
            self.console.print("3. 🔍 Advanced Search Demo (Search capabilities)")
            self.console.print("4. 📊 Memory Analytics (Export and insights)")
            self.console.print("5. 🔄 Batch Operations Demo (Bulk operations)")
            self.console.print("6. 🧪 Advanced Use Cases (Real-world scenarios)")
            self.console.print("7. 📈 Memory Quality & Feedback (Quality control)")
            self.console.print("8. 🚪 Exit")
            
            choice = Prompt.ask("Select mode", choices=["1", "2", "3", "4", "5", "6", "7", "8"])
            
            if choice == "1":
                self._interactive_chat_mode()
            elif choice == "2":
                self._feature_showcase_mode()
            elif choice == "3":
                self._advanced_search_demo()
            elif choice == "4":
                self._memory_analytics_demo()
            elif choice == "5":
                self._batch_operations_demo()
            elif choice == "6":
                self._advanced_use_cases_demo()
            elif choice == "7":
                self._memory_quality_demo()
            elif choice == "8":
                self.console.print("[yellow]👋 Thanks for exploring Mem0 + CAMEL AI![/yellow]")
                break

    def _display_available_tools(self):
        """Display all available tools in a nice table."""
        table = Table(title="🛠️ Enhanced Mem0CloudToolkit - Available Tools")
        table.add_column("Category", style="cyan", no_wrap=True)
        table.add_column("Tool", style="green")
        table.add_column("Description", style="white")
        
        tool_categories = {
            "Core Operations": [
                ("add_memory", "Store new memories with advanced options"),
                ("get_memory", "Retrieve specific memory by ID"),
                ("retrieve_memories", "Get all memories with filtering"),
                ("search_memories", "Advanced semantic search"),
                ("update_memory", "Modify existing memories"),
                ("delete_memory", "Remove specific memory"),
                ("delete_memories", "Bulk delete with filters")
            ],
            "History & Tracking": [
                ("get_memory_history", "Track memory changes over time")
            ],
            "Entity Management": [
                ("get_users", "List all entities with memories"),
                ("delete_users", "Clean up entity data")
            ],
            "System Operations": [
                ("reset_memory", "Complete system reset")
            ],
            "Batch Operations": [
                ("batch_update_memories", "Efficient bulk updates"),
                ("batch_delete_memories", "Efficient bulk deletions")
            ],
            "Quality Control": [
                ("provide_feedback", "Memory quality feedback")
            ],
            "Export & Analytics": [
                ("create_memory_export", "Create structured exports"),
                ("get_memory_export", "Retrieve exported data"),
                ("get_memory_summary", "Analytics and insights")
            ]
        }
        
        for category, tools in tool_categories.items():
            for i, (tool_name, description) in enumerate(tools):
                table.add_row(
                    category if i == 0 else "",
                    tool_name,
                    description
                )
        
        self.console.print(table)
        self.console.print(f"\n[bold green]✨ Total Tools Available: {len(self.tools)}[/bold green]")

    def _interactive_chat_mode(self):
        """Full interactive chat experience with memory persistence."""
        self.console.print(Panel.fit(
            "[bold green]💬 Interactive Chat Mode[/bold green]\n"
            "[dim]Full conversational experience with persistent memory[/dim]",
            border_style="green"
        ))
        
        self.console.print("[dim]Type 'exit', 'quit', or 'help' for special commands[/dim]\n")
        
        # Load conversation context
        self._load_conversation_context()
        
        while True:
            try:
                user_input = Prompt.ask("\n[bold blue]You[/bold blue]")
                
                if user_input.lower() in ["exit", "quit"]:
                    # Save conversation before exit
                    self._save_conversation_context()
                    self.console.print("[yellow]💾 Conversation saved to memory. Goodbye![/yellow]")
                    break
                elif user_input.lower() == "help":
                    self._show_chat_help()
                    continue
                
                # Process user message with full agent capabilities
                user_msg = BaseMessage.make_user_message(
                    role_name="User", 
                    content=user_input
                )
                
                # Show typing indicator
                with self.console.status("[bold green]🧠 Agent thinking...[/bold green]"):
                    response = self.agent.step(user_msg)
                
                # Display agent response
                self.console.print(f"\n[bold green]🤖 Mem0 Agent:[/bold green] {response.msg.content}")
                
                # Track conversation
                self.conversation_history.append({
                    "timestamp": datetime.now().isoformat(),
                    "user": user_input,
                    "agent": response.msg.content
                })
                
            except KeyboardInterrupt:
                self.console.print("\n[yellow]Chat interrupted. Type 'exit' to quit properly.[/yellow]")
                continue

    def _feature_showcase_mode(self):
        """Systematic demonstration of all toolkit features."""
        self.console.print(Panel.fit(
            "[bold magenta]🎯 Feature Showcase Mode[/bold magenta]\n"
            "[dim]Systematic demonstration of all toolkit capabilities[/dim]",
            border_style="magenta"
        ))
        
        features = [
            ("Core Memory Operations", self._demo_core_operations),
            ("Advanced Search Features", self._demo_search_features),
            ("Entity Management", self._demo_entity_management),
            ("Batch Operations", self._demo_batch_features),
            ("Memory History & Tracking", self._demo_history_features),
            ("Export & Analytics", self._demo_export_features),
            ("Quality Control", self._demo_quality_features)
        ]
        
        for feature_name, demo_func in features:
            if Confirm.ask(f"\n🎭 Demonstrate {feature_name}?"):
                self.console.print(f"\n[bold cyan]--- {feature_name} Demo ---[/bold cyan]")
                demo_func()
                self.console.print("[green]✅ Demo completed![/green]")

    def _demo_core_operations(self):
        """Demonstrate core memory operations."""
        operations = [
            ("Adding Memory with Metadata", """
                Add a memory about user preferences with detailed metadata.
                Include category, priority, and timestamp information.
                """),
            ("Retrieving All Memories", """
                Get all stored memories for this user and agent.
                Show pagination and filtering options.
                """),
            ("Searching Memories", """
                Search for memories about 'preferences' using semantic search.
                Use advanced filters and threshold settings.
                """),
            ("Updating Memory", """
                Update an existing memory with new information.
                Demonstrate both text and metadata updates.
                """),
            ("Getting Specific Memory", """
                Retrieve a specific memory by its unique ID.
                Show detailed memory information.
                """)
        ]
        
        for operation, description in operations:
            self.console.print(f"\n[bold yellow]🔧 {operation}:[/bold yellow]")
            self.console.print(f"[dim]{description.strip()}[/dim]")
            
            if Confirm.ask("Execute this operation?"):
                # Use the agent to perform the operation
                user_msg = BaseMessage.make_user_message(
                    role_name="User",
                    content=description.strip()
                )
                response = self.agent.step(user_msg)
                self.console.print(f"[green]🤖 Agent:[/green] {response.msg.content}")

    def _demo_search_features(self):
        """Demonstrate advanced search capabilities."""
        # First, add some test memories for searching
        test_memories = [
            "I love playing chess on weekends and participate in local tournaments",
            "My favorite programming language is Python, especially for data science",
            "I work as a software engineer at a tech startup in San Francisco",
            "I enjoy hiking in the mountains and camping during summer",
            "My morning routine includes yoga, meditation, and reading"
        ]
        
        self.console.print("[cyan]📝 Adding test memories for search demonstration...[/cyan]")
        for memory in test_memories:
            user_msg = BaseMessage.make_user_message(
                role_name="User",
                content=f"Please add this memory: {memory}"
            )
            self.agent.step(user_msg)
        
        # Demonstrate different search patterns
        search_queries = [
            ("Basic Semantic Search", "hobbies and interests"),
            ("Work-related Search", "career and job"),
            ("Activity Search with High Threshold", "outdoor activities"),
            ("Programming Search with Filters", "coding and development"),
            ("Morning Routine Search", "daily habits")
        ]
        
        for search_type, query in search_queries:
            self.console.print(f"\n[bold blue]🔍 {search_type}:[/bold blue]")
            self.console.print(f"[dim]Query: '{query}'[/dim]")
            
            user_msg = BaseMessage.make_user_message(
                role_name="User",
                content=f"Search my memories for: {query}. Use advanced search features."
            )
            response = self.agent.step(user_msg)
            self.console.print(f"[green]Results:[/green] {response.msg.content}")

    def _demo_entity_management(self):
        """Demonstrate entity management features."""
        operations = [
            ("List All Entities", "Show me all users, agents, and sessions with memories"),
            ("Entity Analytics", "Analyze the memory distribution across entities"),
            ("Entity Cleanup", "Show how to clean up specific entity data")
        ]
        
        for operation, query in operations:
            self.console.print(f"\n[bold purple]👥 {operation}:[/bold purple]")
            
            user_msg = BaseMessage.make_user_message(role_name="User", content=query)
            response = self.agent.step(user_msg)
            self.console.print(f"[green]Result:[/green] {response.msg.content}")

    def _demo_batch_features(self):
        """Demonstrate batch operations."""
        if Confirm.ask("Create test memories for batch operations demo?"):
            # Create multiple memories for batch operations
            self.console.print("[cyan]📝 Creating test memories...[/cyan]")
            
            batch_memories = [
                "Project Alpha: Initial planning phase completed",
                "Project Alpha: Design mockups approved by client", 
                "Project Alpha: Development started on core features",
                "Project Beta: Requirements gathering in progress",
                "Project Beta: Technical architecture designed"
            ]
            
            memory_ids = []
            for memory in batch_memories:
                user_msg = BaseMessage.make_user_message(
                    role_name="User",
                    content=f"Add this memory and return the memory ID: {memory}"
                )
                response = self.agent.step(user_msg)
                # Note: In a real implementation, you'd extract the memory ID from the response
                
            # Demonstrate batch update
            self.console.print("\n[bold orange]🔄 Batch Update Demo:[/bold orange]")
            user_msg = BaseMessage.make_user_message(
                role_name="User",
                content="Show me how to perform batch updates on multiple memories at once. Explain the process and benefits."
            )
            response = self.agent.step(user_msg)
            self.console.print(f"[green]Agent:[/green] {response.msg.content}")

    def _demo_history_features(self):
        """Demonstrate memory history and tracking."""
        operations = [
            "Show me how memory history tracking works",
            "Explain how to view changes to a specific memory over time",
            "Demonstrate memory versioning and audit trails"
        ]
        
        for query in operations:
            self.console.print(f"\n[bold teal]📚 History Demo:[/bold teal]")
            self.console.print(f"[dim]{query}[/dim]")
            
            user_msg = BaseMessage.make_user_message(role_name="User", content=query)
            response = self.agent.step(user_msg)
            self.console.print(f"[green]Agent:[/green] {response.msg.content}")

    def _demo_export_features(self):
        """Demonstrate export and analytics capabilities."""
        export_demos = [
            ("Create Memory Export", "Create a structured export of my memories with a custom schema"),
            ("Memory Analytics", "Generate analytics and insights about my memory patterns"),
            ("Export Retrieval", "Show how to retrieve and work with exported memory data")
        ]
        
        for demo_name, query in export_demos:
            self.console.print(f"\n[bold gold1]📊 {demo_name}:[/bold gold1]")
            
            user_msg = BaseMessage.make_user_message(role_name="User", content=query)
            response = self.agent.step(user_msg)
            self.console.print(f"[green]Agent:[/green] {response.msg.content}")

    def _demo_quality_features(self):
        """Demonstrate quality control and feedback features."""
        quality_operations = [
            "Explain how memory feedback works for quality improvement",
            "Show different types of feedback (positive, negative) and their purposes",
            "Demonstrate how feedback helps improve memory relevance and accuracy"
        ]
        
        for query in quality_operations:
            self.console.print(f"\n[bold red]⭐ Quality Control:[/bold red]")
            self.console.print(f"[dim]{query}[/dim]")
            
            user_msg = BaseMessage.make_user_message(role_name="User", content=query)
            response = self.agent.step(user_msg)
            self.console.print(f"[green]Agent:[/green] {response.msg.content}")

    def _advanced_search_demo(self):
        """Advanced search patterns and techniques."""
        self.console.print(Panel.fit(
            "[bold blue]🔍 Advanced Search Demonstration[/bold blue]\n"
            "[dim]Exploring sophisticated search patterns and techniques[/dim]",
            border_style="blue"
        ))
        
        # Create comprehensive test data
        self._create_comprehensive_test_data()
        
        advanced_searches = [
            ("Multi-Filter Search", "Search for work-related memories from the last month with high priority"),
            ("Semantic Clustering", "Find memories related to 'productivity' and group similar concepts"),
            ("Threshold-based Search", "Search with different similarity thresholds to compare results"),
            ("Metadata-rich Search", "Search using complex metadata filters and conditions"),
            ("Cross-entity Search", "Search across different users and agents for comparative analysis")
        ]
        
        for search_type, description in advanced_searches:
            self.console.print(f"\n[bold cyan]🔍 {search_type}:[/bold cyan]")
            self.console.print(f"[dim]{description}[/dim]")
            
            if Confirm.ask("Execute this search?"):
                user_msg = BaseMessage.make_user_message(role_name="User", content=description)
                response = self.agent.step(user_msg)
                self.console.print(f"[green]Results:[/green] {response.msg.content}")

    def _memory_analytics_demo(self):
        """Comprehensive memory analytics demonstration."""
        self.console.print(Panel.fit(
            "[bold green]📊 Memory Analytics & Insights[/bold green]\n"
            "[dim]Advanced analytics, export, and memory intelligence[/dim]",
            border_style="green"
        ))
        
        analytics_operations = [
            ("Memory Distribution Analysis", "Analyze how memories are distributed across categories and time"),
            ("Search Pattern Analytics", "Analyze what types of information are most frequently searched"),
            ("Memory Quality Metrics", "Evaluate memory quality and relevance scores"),
            ("Usage Pattern Insights", "Identify trends in memory usage and access patterns"),
            ("Export Summary Report", "Generate a comprehensive summary report of all memory data")
        ]
        
        for operation, description in analytics_operations:
            self.console.print(f"\n[bold magenta]📈 {operation}:[/bold magenta]")
            
            if Confirm.ask(f"Run {operation}?"):
                user_msg = BaseMessage.make_user_message(role_name="User", content=description)
                response = self.agent.step(user_msg)
                self.console.print(f"[green]Analysis:[/green] {response.msg.content}")

    def _batch_operations_demo(self):
        """Comprehensive batch operations demonstration."""
        self.console.print(Panel.fit(
            "[bold orange]🔄 Batch Operations Mastery[/bold orange]\n"
            "[dim]Efficient bulk operations for large-scale memory management[/dim]",
            border_style="orange"
        ))
        
        # Create test data for batch operations
        if Confirm.ask("Create test dataset for batch operations?"):
            self._create_batch_test_data()
        
        batch_demos = [
            ("Batch Memory Creation", "Create multiple related memories efficiently"),
            ("Bulk Update Operations", "Update multiple memories with new information"),
            ("Conditional Batch Delete", "Delete memories based on specific criteria"),
            ("Batch Metadata Updates", "Update metadata across multiple memories"),
            ("Performance Comparison", "Compare batch vs individual operations performance")
        ]
        
        for demo_name, description in batch_demos:
            self.console.print(f"\n[bold yellow]⚡ {demo_name}:[/bold yellow]")
            
            if Confirm.ask(f"Execute {demo_name}?"):
                user_msg = BaseMessage.make_user_message(role_name="User", content=description)
                response = self.agent.step(user_msg)
                self.console.print(f"[green]Result:[/green] {response.msg.content}")

    def _advanced_use_cases_demo(self):
        """Real-world use case demonstrations."""
        self.console.print(Panel.fit(
            "[bold purple]🧪 Advanced Use Cases[/bold purple]\n"
            "[dim]Real-world scenarios and advanced memory patterns[/dim]",
            border_style="purple"
        ))
        
        use_cases = [
            ("Personal AI Assistant", "Demonstrate how to build a personal AI assistant with memory"),
            ("Knowledge Management System", "Show enterprise knowledge management capabilities"),
            ("Customer Support Agent", "Build a support agent that remembers customer interactions"),
            ("Learning Companion", "Create an AI tutor that tracks learning progress"),
            ("Project Management Assistant", "Manage complex projects with memory-enabled AI")
        ]
        
        for use_case, description in use_cases:
            self.console.print(f"\n[bold bright_blue]🎯 {use_case}:[/bold bright_blue]")
            
            if Confirm.ask(f"Explore {use_case}?"):
                self._demonstrate_use_case(use_case, description)

    def _memory_quality_demo(self):
        """Memory quality and feedback demonstration."""
        self.console.print(Panel.fit(
            "[bold red]📈 Memory Quality & Feedback[/bold red]\n"
            "[dim]Quality control, feedback mechanisms, and memory improvement[/dim]",
            border_style="red"
        ))
        
        quality_aspects = [
            ("Memory Feedback System", "Learn how to provide feedback on memory quality"),
            ("Quality Scoring", "Understand memory relevance and accuracy scoring"),
            ("Feedback Analytics", "Analyze feedback patterns to improve memory systems"),
            ("Quality Improvement", "Implement strategies for better memory quality"),
            ("Feedback Loops", "Create continuous improvement cycles")
        ]
        
        for aspect, description in quality_aspects:
            self.console.print(f"\n[bold bright_red]⭐ {aspect}:[/bold bright_red]")
            
            if Confirm.ask(f"Explore {aspect}?"):
                user_msg = BaseMessage.make_user_message(role_name="User", content=description)
                response = self.agent.step(user_msg)
                self.console.print(f"[green]Insights:[/green] {response.msg.content}")

    def _create_comprehensive_test_data(self):
        """Create comprehensive test data for demonstrations."""
        self.console.print("[cyan]📝 Creating comprehensive test data...[/cyan]")
        
        test_data = [
            # Work-related memories
            {"content": "Project Alpha milestone completed ahead of schedule", 
             "metadata": {"category": "work", "project": "alpha", "priority": "high", "date": "2024-01-15"}},
            {"content": "Weekly team meeting scheduled for Mondays at 10 AM", 
             "metadata": {"category": "work", "type": "meeting", "recurring": True}},
            {"content": "Client feedback: They love the new dashboard design", 
             "metadata": {"category": "work", "type": "feedback", "sentiment": "positive"}},
            
            # Personal memories
            {"content": "Finished reading 'Deep Work' by Cal Newport - great insights on focus", 
             "metadata": {"category": "personal", "type": "learning", "topic": "productivity"}},
            {"content": "Morning routine: 6 AM wake up, exercise, meditation, breakfast", 
             "metadata": {"category": "personal", "type": "routine", "time": "morning"}},
            {"content": "Favorite coffee shop: Blue Bottle on Market Street", 
             "metadata": {"category": "personal", "type": "preference", "location": "San Francisco"}},
            
            # Technical memories
            {"content": "Learned about vector embeddings for semantic search implementation", 
             "metadata": {"category": "technical", "topic": "AI", "complexity": "advanced"}},
            {"content": "Python best practices: Use type hints and docstrings", 
             "metadata": {"category": "technical", "language": "python", "type": "best_practice"}},
            {"content": "Database optimization reduced query time by 60%", 
             "metadata": {"category": "technical", "type": "performance", "improvement": "60%"}},
        ]
        
        for data in test_data:
            user_msg = BaseMessage.make_user_message(
                role_name="User",
                content=f"Add this memory with metadata: {data['content']} | Metadata: {json.dumps(data['metadata'])}"
            )
            self.agent.step(user_msg)
        
        self.console.print(f"[green]✅ Created {len(test_data)} test memories with rich metadata[/green]")

    def _create_batch_test_data(self):
        """Create test data specifically for batch operations."""
        self.console.print("[cyan]📦 Creating batch operation test data...[/cyan]")
        
        user_msg = BaseMessage.make_user_message(
            role_name="User",
            content="""Create 10 test memories for batch operations demo. Include:
            - 5 memories about different projects (Alpha, Beta, Gamma, Delta, Echo)
            - 3 memories about team members and their skills
            - 2 memories about company policies and procedures
            Use varied metadata for each memory including project names, priorities, and dates."""
        )
        
        response = self.agent.step(user_msg)
        self.console.print(f"[green]✅ Batch test data created:[/green] {response.msg.content}")

    def _demonstrate_use_case(self, use_case: str, description: str):
        """Demonstrate a specific real-world use case."""
        self.console.print(f"\n[bold cyan]🎭 Demonstrating: {use_case}[/bold cyan]")
        self.console.print(f"[dim]{description}[/dim]")
        
        # Create scenario-specific prompts
        scenarios = {
            "Personal AI Assistant": [
                "Set up a personal AI assistant that remembers my preferences, schedule, and habits",
                "Show how the assistant can proactively suggest actions based on memory patterns",
                "Demonstrate context-aware responses using historical conversation data"
            ],
            "Knowledge Management System": [
                "Create a knowledge base with categorized information and expert insights",
                "Demonstrate semantic search across different knowledge domains",
                "Show how to maintain and update knowledge with version control"
            ],
            "Customer Support Agent": [
                "Build a support agent that remembers customer interaction history",
                "Demonstrate personalized support based on previous tickets and preferences",
                "Show escalation patterns and resolution tracking"
            ],
            "Learning Companion": [
                "Create an AI tutor that tracks learning progress and adapts to student needs",
                "Demonstrate personalized curriculum based on learning patterns",
                "Show how to identify knowledge gaps and provide targeted support"
            ],
            "Project Management Assistant": [
                "Build a PM assistant that tracks project milestones, team assignments, and deadlines",
                "Demonstrate resource allocation and timeline optimization",
                "Show risk assessment based on historical project data"
            ]
        }
        
        if use_case in scenarios:
            for i, scenario in enumerate(scenarios[use_case], 1):
                self.console.print(f"\n[bold yellow]Step {i}:[/bold yellow] {scenario}")
                
                if Confirm.ask(f"Execute step {i}?"):
                    user_msg = BaseMessage.make_user_message(role_name="User", content=scenario)
                    response = self.agent.step(user_msg)
                    self.console.print(f"[green]Result:[/green] {response.msg.content}")

    def _load_conversation_context(self):
        """Load previous conversation context from memory."""
        user_msg = BaseMessage.make_user_message(
            role_name="User",
            content="Search for any previous conversation history and load the context. Summarize what we've discussed before."
        )
        response = self.agent.step(user_msg)
        
        if "no previous" not in response.msg.content.lower():
            self.console.print(f"[dim]📚 Previous context loaded:[/dim] {response.msg.content}")

    def _save_conversation_context(self):
        """Save current conversation context to memory."""
        if self.conversation_history:
            conversation_summary = f"Conversation session ended at {datetime.now().isoformat()}. " \
                                 f"Total exchanges: {len(self.conversation_history)}. " \
                                 f"Key topics discussed: {', '.join([entry['user'][:50] + '...' for entry in self.conversation_history[-3:]])}"
            
            user_msg = BaseMessage.make_user_message(
                role_name="User",
                content=f"Save this conversation summary to memory: {conversation_summary}"
            )
            self.agent.step(user_msg)

    def _show_chat_help(self):
        """Show help information for chat mode."""
        help_text = """
[bold cyan]💬 Chat Mode Help[/bold cyan]

[bold]Available Commands:[/bold]
• [green]exit/quit[/green] - End the conversation and save context
• [green]help[/green] - Show this help message

[bold]Memory Operations You Can Try:[/bold]
• "Remember that I prefer morning meetings"
• "What do you know about my work preferences?"
• "Search for information about my hobbies"
• "Update my coffee preference"
• "Show me my memory history"
• "Export my memories as a summary"
• "Give feedback on a specific memory"
• "Delete old memories about X topic"

[bold]Advanced Features:[/bold]
• Ask for batch operations on multiple memories
• Request memory analytics and insights
• Explore entity management features
• Try complex search queries with filters

[bold]Tips:[/bold]
• Be specific about what you want to remember or retrieve
• Ask the agent to explain what memory tools it's using
• Try conversational memory management
"""
        self.console.print(Panel(help_text, border_style="cyan"))


def setup_environment():
    """Setup environment and check requirements."""
    console = Console()
    
    console.print(Panel.fit(
        "[bold blue]🚀 Mem0 + CAMEL AI Setup[/bold blue]\n"
        "[dim]Checking environment and requirements[/dim]",
        border_style="blue"
    ))
    
    # Check for required environment variables
    required_vars = ["MEM0_API_KEY", "OPENAI_API_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        console.print(f"[red]❌ Missing environment variables: {', '.join(missing_vars)}[/red]")
        console.print("\n[yellow]Please set the following environment variables:[/yellow]")
        for var in missing_vars:
            if var == "MEM0_API_KEY":
                console.print(f"• {var}: Get it from https://app.mem0.ai/dashboard/api-keys")
            elif var == "OPENAI_API_KEY":
                console.print(f"• {var}: Get it from https://platform.openai.com/api-keys")
        return False
    
    # Verify toolkit is available
    try:
        from mem_camel_toolkit import Mem0CloudToolkit
        console.print("[green]✅ Mem0CloudToolkit loaded successfully[/green]")
    except ImportError as e:
        console.print(f"[red]❌ Failed to import Mem0CloudToolkit: {e}[/red]")
        console.print("[yellow]Please ensure mem_camel_toolkit.py is in your Python path[/yellow]")
        return False
    
    console.print("[green]✅ Environment setup complete![/green]")
    return True


def main():
    """Main function to run the comprehensive demo."""
    console = Console()
    
    # ASCII Art Header
    console.print("""
[bold blue]
╔══════════════════════════════════════════════════════════════════════════════╗
║                     🧠 MEM0 + CAMEL AI COMPREHENSIVE DEMO                   ║
║                                                                              ║
║  Enhanced Memory Toolkit with 18+ Advanced Features                         ║
║  • Core Operations  • Advanced Search  • Batch Processing                   ║
║  • Entity Management  • Export & Analytics  • Quality Control               ║
╚══════════════════════════════════════════════════════════════════════════════╝
[/bold blue]
    """)
    
    # Setup environment
    if not setup_environment():
        return
    
    # Initialize and start the comprehensive demo
    try:
        agent = ComprehensiveMemoryAgent()
        agent.start_comprehensive_demo()
    except KeyboardInterrupt:
        console.print("\n[yellow]👋 Demo interrupted. Goodbye![/yellow]")
    except Exception as e:
        console.print(f"\n[red]❌ Error: {e}[/red]")
        console.print("[dim]Please check your environment setup and try again.[/dim]")


if __name__ == "__main__":
    main()