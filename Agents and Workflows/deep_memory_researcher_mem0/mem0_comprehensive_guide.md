# 🧠 Mem0 Python SDK - Complete Usage Guide & Examples

A comprehensive guide showcasing all functionalities of the Mem0 Python SDK with practical examples and advanced search use cases.

---

## 📋 Table of Contents

1. [Setup & Installation](#setup--installation)
2. [Cloud Client - Basic Operations](#cloud-client---basic-operations)
3. [Cloud Client - Advanced Search](#cloud-client---advanced-search)
4. [Cloud Client - Batch Operations](#cloud-client---batch-operations)
5. [Cloud Client - Entity Management](#cloud-client---entity-management)
6. [Cloud Client - Export & Analytics](#cloud-client---export--analytics)
7. [Local Memory - Complete Guide](#local-memory---complete-guide)
8. [Advanced Search Patterns](#advanced-search-patterns)
9. [Real-World Use Cases](#real-world-use-cases)

---

## Setup & Installation

```python
# Install Mem0
!pip install mem0ai

import os
from mem0 import MemoryClient, Memory
import json
from datetime import datetime
```

```python
# Cloud Client Setup
os.environ["MEM0_API_KEY"] = "your-api-key-here"  # Get from https://app.mem0.ai
client = MemoryClient()
```

```python
# Local Memory Setup (Self-hosted)
config = {
    "llm": {
        "provider": "openai",
        "config": {
            "model": "gpt-4o-mini",
            "temperature": 0.2,
            "api_key": os.getenv("OPENAI_API_KEY")
        }
    },
    "embedder": {
        "provider": "openai",
        "config": {
            "model": "text-embedding-3-small"
        }
    },
    "vector_store": {
        "provider": "qdrant",
        "config": {
            "collection_name": "mem0_db",
            "host": "localhost",
            "port": 6333
        }
    },
    "version": "v1.1"
}

memory = Memory.from_config(config)
```

---

## Cloud Client - Basic Operations

### 🎯 Adding Memories

```python
# Simple text memory
messages = [{"role": "user", "content": "I love playing chess on weekends"}]
result = client.add(messages, user_id="alice")
print("Added memory:", result)
```

```python
# Conversational memory with context
conversation = [
    {"role": "user", "content": "My name is Bob"},
    {"role": "assistant", "content": "Nice to meet you, Bob!"},
    {"role": "user", "content": "I work at Google as a software engineer"},
    {"role": "assistant", "content": "That's impressive! Software engineering at Google must be exciting."}
]

result = client.add(
    messages=conversation,
    user_id="bob_engineer",
    metadata={
        "conversation_id": "conv_001",
        "topic": "introduction",
        "timestamp": datetime.now().isoformat()
    },
    output_format="v1.1"
)
print("Conversation memory added:", result)
```

```python
# Agent-specific memory
agent_memory = [
    {"role": "user", "content": "Set reminder for daily standup at 9 AM"},
    {"role": "assistant", "content": "Daily standup reminder set for 9 AM"}
]

result = client.add(
    messages=agent_memory,
    agent_id="productivity_agent",
    user_id="team_lead",
    metadata={
        "category": "reminders",
        "priority": "high",
        "recurring": True
    }
)
print("Agent memory added:", result)
```

### 📖 Retrieving Memories

```python
# Get specific memory by ID
memory_id = "mem_12345"  # Replace with actual memory ID
memory = client.get(memory_id)
print("Retrieved memory:", memory)
```

```python
# Get all memories for a user (v1)
user_memories = client.get_all(user_id="alice", version="v1")
print(f"User memories (v1): {len(user_memories)} memories found")
for memory in user_memories[:3]:  # Show first 3
    print(f"- {memory.get('memory', 'N/A')}")
```

```python
# Get all memories with pagination (v2)
paginated_memories = client.get_all(
    user_id="bob_engineer",
    version="v2",
    page=1,
    page_size=5
)
print("Paginated memories:", paginated_memories)
```

```python
# Get memories with filters
filtered_memories = client.get_all(
    agent_id="productivity_agent",
    metadata={"category": "reminders"},
    version="v2"
)
print("Filtered agent memories:", filtered_memories)
```

### ✏️ Updating & Deleting Memories

```python
# Update memory content
memory_id = "mem_12345"
updated = client.update(
    memory_id=memory_id,
    text="I love playing chess on weekends and also enjoy online tournaments"
)
print("Memory updated:", updated)
```

```python
# Update memory metadata
metadata_updated = client.update(
    memory_id=memory_id,
    metadata={
        "hobby": "chess",
        "skill_level": "intermediate",
        "last_updated": datetime.now().isoformat()
    }
)
print("Metadata updated:", metadata_updated)
```

```python
# Delete specific memory
deleted = client.delete(memory_id)
print("Memory deleted:", deleted)
```

```python
# Delete all memories for a user
user_cleanup = client.delete_all(user_id="alice")
print("User memories deleted:", user_cleanup)
```

---

## Cloud Client - Advanced Search

### 🔍 Basic Search Operations

```python
# Simple semantic search
search_results = client.search(
    query="chess games",
    user_id="alice",
    version="v1"
)
print("Search results:", search_results)
```

```python
# Advanced search with filters (v2)
advanced_search = client.search(
    query="work meetings",
    user_id="bob_engineer",
    version="v2",
    filters={"category": "reminders"},
    limit=5,
    rerank=True,
    threshold=0.7
)
print("Advanced search results:", advanced_search)
```

### 🎯 Complex Search Patterns

```python
# Multi-user search with OR conditions
multi_user_search = client.search(
    query="programming languages",
    version="v2",
    filters={
        "OR": [
            {"user_id": "bob_engineer"},
            {"user_id": "alice_dev"},
            {"agent_id": "coding_assistant"}
        ]
    },
    limit=10,
    rerank=True
)
print("Multi-user search:", multi_user_search)
```

```python
# Temporal search with date ranges
temporal_search = client.search(
    query="project updates",
    version="v2",
    filters={
        "AND": [
            {"user_id": "team_lead"},
            {"metadata.timestamp": {"gte": "2024-01-01", "lte": "2024-12-31"}},
            {"metadata.category": "work"}
        ]
    },
    limit=15
)
print("Temporal search:", temporal_search)
```

```python
# Contextual search with metadata filtering
contextual_search = client.search(
    query="customer feedback",
    version="v2",
    filters={
        "metadata.priority": "high",
        "metadata.status": "open",
        "agent_id": "support_agent"
    },
    threshold=0.6,
    limit=20
)
print("Contextual search:", contextual_search)
```

### 📊 Search Analytics & Scoring

```python
# Search with custom scoring and ranking
scored_search = client.search(
    query="machine learning projects",
    version="v2",
    user_id="data_scientist",
    threshold=0.5,
    limit=8,
    rerank=True,
    filters={
        "metadata.domain": "AI",
        "metadata.status": "active"
    }
)

# Analyze search results
print("Search Analytics:")
for i, result in enumerate(scored_search.get('results', []), 1):
    score = result.get('score', 0)
    memory_text = result.get('memory', '')
    print(f"{i}. Score: {score:.3f} | Memory: {memory_text[:60]}...")
```

---

## Cloud Client - Batch Operations

### 🔄 Batch Updates

```python
# Prepare batch update data
batch_updates = [
    {
        "memory_id": "mem_001",
        "text": "Updated: I love playing chess and participate in tournaments"
    },
    {
        "memory_id": "mem_002", 
        "text": "Updated: Work at Google as Senior Software Engineer"
    },
    {
        "memory_id": "mem_003",
        "text": "Updated: Daily standup moved to 9:30 AM"
    }
]

# Execute batch update
batch_result = client.batch_update(batch_updates)
print("Batch update result:", batch_result)
```

### 🗑️ Batch Deletions

```python
# Prepare batch deletion data
batch_deletions = [
    {"memory_id": "mem_004"},
    {"memory_id": "mem_005"},
    {"memory_id": "mem_006"}
]

# Execute batch deletion
batch_delete_result = client.batch_delete(batch_deletions)
print("Batch deletion result:", batch_delete_result)
```

---

## Cloud Client - Entity Management

### 👥 User & Entity Operations

```python
# Get all entities (users, agents, sessions)
entities = client.users()
print("All entities:", entities)
```

```python
# Delete specific user data
user_deletion = client.delete_users(user_id="alice")
print("User deleted:", user_deletion)
```

```python
# Delete specific agent data
agent_deletion = client.delete_users(agent_id="old_assistant")
print("Agent deleted:", agent_deletion)
```

```python
# Complete system reset
reset_result = client.reset()
print("System reset:", reset_result)
```

### 📈 Memory History & Feedback

```python
# Get memory history
memory_history = client.history("mem_12345")
print("Memory history:", memory_history)
```

```python
# Provide feedback on memory quality
feedback_result = client.feedback(
    memory_id="mem_12345",
    feedback="POSITIVE",
    feedback_reason="Accurate and relevant information"
)
print("Feedback submitted:", feedback_result)
```

```python
# Negative feedback example
negative_feedback = client.feedback(
    memory_id="mem_67890",
    feedback="NEGATIVE", 
    feedback_reason="Information is outdated and no longer relevant"
)
print("Negative feedback:", negative_feedback)
```

---

## Cloud Client - Export & Analytics

### 📤 Memory Export

```python
# Define export schema
export_schema = json.dumps({
    "type": "object",
    "properties": {
        "memories": {
            "type": "array",
            "items": {
                "type": "object", 
                "properties": {
                    "id": {"type": "string"},
                    "content": {"type": "string"},
                    "metadata": {"type": "object"},
                    "timestamp": {"type": "string"}
                }
            }
        },
        "total_count": {"type": "integer"},
        "export_date": {"type": "string"}
    }
})

# Create export
export_request = client.create_memory_export(
    schema=export_schema,
    user_id="bob_engineer",
    filters={"metadata.category": "work"}
)
print("Export created:", export_request)
```

```python
# Retrieve export data
export_data = client.get_memory_export(user_id="bob_engineer")
print("Export data:", export_data)
```

```python
# Get memory summary and analytics
summary = client.get_summary(
    filters={
        "user_id": "team_lead",
        "metadata.category": "meetings"
    }
)
print("Memory summary:", summary)
```

---

## Local Memory - Complete Guide

### 🏠 Local Memory Operations

```python
# Add memories to local storage
local_add = memory.add(
    messages="I prefer working remotely and love collaborative tools",
    user_id="remote_worker",
    metadata={"work_style": "remote", "tools": ["slack", "zoom", "notion"]}
)
print("Local memory added:", local_add)
```

```python
# Advanced local memory with inference control
structured_memory = memory.add(
    messages=[
        {"role": "user", "content": "I have a meeting with the design team tomorrow at 3 PM"},
        {"role": "assistant", "content": "I'll help you prepare for the design team meeting"}
    ],
    user_id="project_manager",
    infer=True,  # Enable AI-powered fact extraction
    metadata={
        "event_type": "meeting",
        "participants": ["design_team"],
        "datetime": "2024-12-13T15:00:00"
    }
)
print("Structured local memory:", structured_memory)
```

### 🔍 Local Search with Thresholds

```python
# Local search with similarity threshold
local_search = memory.search(
    query="remote work tools",
    user_id="remote_worker",
    threshold=0.7,
    limit=5
)
print("Local search results:", local_search)
```

```python
# Get all local memories with filters
all_local = memory.get_all(
    user_id="project_manager",
    filters={"event_type": "meeting"},
    limit=10
)
print("All local memories:", all_local)
```

### 🛠️ Local Memory Management

```python
# Update local memory
local_update = memory.update(
    memory_id="local_mem_123",
    data="I prefer working remotely and use collaborative tools like Slack, Zoom, and Notion daily"
)
print("Local memory updated:", local_update)
```

```python
# Delete local memory
local_delete = memory.delete("local_mem_123")
print("Local memory deleted:", local_delete)
```

```python
# Local memory history
local_history = memory.history("local_mem_456")
print("Local memory history:", local_history)
```

---

## Advanced Search Patterns

### 🧪 Experimental Search Techniques

```python
# Semantic similarity clustering
def semantic_clustering_search(client, base_query, user_id):
    """Find memories semantically similar to base query and cluster them"""
    
    # Initial search
    base_results = client.search(
        query=base_query,
        user_id=user_id,
        version="v2",
        limit=20,
        threshold=0.6
    )
    
    # Extract key concepts for related searches
    related_queries = [
        f"{base_query} related topics",
        f"{base_query} similar concepts",
        f"{base_query} connected ideas"
    ]
    
    clustered_results = {"base": base_results}
    
    for i, related_query in enumerate(related_queries):
        related_results = client.search(
            query=related_query,
            user_id=user_id,
            version="v2",
            limit=10,
            threshold=0.5
        )
        clustered_results[f"cluster_{i+1}"] = related_results
    
    return clustered_results

# Example usage
clusters = semantic_clustering_search(client, "machine learning", "data_scientist")
print("Semantic clusters found:", len(clusters))
```

```python
# Multi-modal search patterns
def multi_modal_search(client, text_query, image_context=None, audio_context=None):
    """Search across different content modalities"""
    
    search_filters = {
        "OR": [
            {"metadata.content_type": "text"},
            {"metadata.content_type": "image"}, 
            {"metadata.content_type": "audio"},
            {"metadata.content_type": "multimodal"}
        ]
    }
    
    if image_context:
        search_filters["metadata.image_tags"] = {"contains": image_context}
    
    if audio_context:
        search_filters["metadata.audio_transcript"] = {"contains": audio_context}
    
    results = client.search(
        query=text_query,
        version="v2",
        filters=search_filters,
        limit=15,
        rerank=True
    )
    
    return results

# Example usage  
multimodal_results = multi_modal_search(
    client, 
    "presentation slides",
    image_context=["charts", "graphs"],
    audio_context=["meeting recording"]
)
print("Multi-modal search results:", multimodal_results)
```

### 📊 Search Result Analysis

```python
def analyze_search_results(search_results):
    """Analyze and categorize search results"""
    
    results = search_results.get('results', [])
    
    analysis = {
        "total_results": len(results),
        "high_confidence": [],  # score > 0.8
        "medium_confidence": [],  # 0.6 < score <= 0.8  
        "low_confidence": [],  # score <= 0.6
        "metadata_categories": {},
        "average_score": 0
    }
    
    total_score = 0
    
    for result in results:
        score = result.get('score', 0)
        total_score += score
        
        # Confidence categorization
        if score > 0.8:
            analysis["high_confidence"].append(result)
        elif score > 0.6:
            analysis["medium_confidence"].append(result)
        else:
            analysis["low_confidence"].append(result)
        
        # Metadata analysis
        metadata = result.get('metadata', {})
        for key, value in metadata.items():
            if key not in analysis["metadata_categories"]:
                analysis["metadata_categories"][key] = {}
            if value not in analysis["metadata_categories"][key]:
                analysis["metadata_categories"][key][value] = 0
            analysis["metadata_categories"][key][value] += 1
    
    if results:
        analysis["average_score"] = total_score / len(results)
    
    return analysis

# Example analysis
search_results = client.search("project updates", user_id="team_lead", limit=20)
analysis = analyze_search_results(search_results)
print("Search Analysis:", json.dumps(analysis, indent=2, default=str))
```

---

## Real-World Use Cases

### 🤖 AI Assistant Memory System

```python
class AIAssistantMemory:
    def __init__(self, client, assistant_id, user_id):
        self.client = client
        self.assistant_id = assistant_id
        self.user_id = user_id
    
    def remember_user_preference(self, preference_type, preference_value, context=None):
        """Store user preferences for personalization"""
        messages = [{
            "role": "user", 
            "content": f"User preference: {preference_type} = {preference_value}"
        }]
        
        if context:
            messages.append({
                "role": "assistant",
                "content": f"Context: {context}"
            })
        
        return self.client.add(
            messages=messages,
            agent_id=self.assistant_id,
            user_id=self.user_id,
            metadata={
                "type": "preference",
                "category": preference_type,
                "value": preference_value,
                "timestamp": datetime.now().isoformat()
            }
        )
    
    def recall_preferences(self, category=None):
        """Retrieve user preferences for context"""
        filters = {"metadata.type": "preference"}
        if category:
            filters["metadata.category"] = category
            
        return self.client.search(
            query=f"user preferences {category or ''}",
            agent_id=self.assistant_id,
            user_id=self.user_id,
            version="v2",
            filters=filters,
            limit=10
        )
    
    def store_conversation_context(self, conversation, topic=None):
        """Store important conversation context"""
        return self.client.add(
            messages=conversation,
            agent_id=self.assistant_id,
            user_id=self.user_id,
            metadata={
                "type": "conversation",
                "topic": topic or "general",
                "timestamp": datetime.now().isoformat()
            }
        )

# Usage example
assistant = AIAssistantMemory(client, "personal_assistant", "john_doe")

# Store preferences
pref_result = assistant.remember_user_preference(
    "communication_style", 
    "brief and direct",
    context="User prefers concise responses during work hours"
)
print("Preference stored:", pref_result)

# Recall preferences
preferences = assistant.recall_preferences("communication_style")
print("User preferences:", preferences)
```

### 📚 Knowledge Management System

```python
class KnowledgeBase:
    def __init__(self, client, domain):
        self.client = client
        self.domain = domain
    
    def add_knowledge(self, content, category, source=None, confidence=None):
        """Add knowledge with categorization"""
        messages = [{"role": "system", "content": f"Knowledge: {content}"}]
        
        metadata = {
            "domain": self.domain,
            "category": category,
            "knowledge_type": "fact",
            "timestamp": datetime.now().isoformat()
        }
        
        if source:
            metadata["source"] = source
        if confidence:
            metadata["confidence"] = confidence
            
        return self.client.add(
            messages=messages,
            agent_id=f"{self.domain}_knowledge_agent",
            metadata=metadata
        )
    
    def query_knowledge(self, question, category=None, min_confidence=0.7):
        """Query the knowledge base"""
        filters = {"metadata.domain": self.domain}
        if category:
            filters["metadata.category"] = category
        if min_confidence:
            filters["metadata.confidence"] = {"gte": min_confidence}
            
        return self.client.search(
            query=question,
            version="v2",
            filters=filters,
            threshold=0.6,
            limit=15,
            rerank=True
        )
    
    def update_knowledge(self, memory_id, new_content, new_confidence=None):
        """Update existing knowledge"""
        update_data = {"text": new_content}
        if new_confidence:
            update_data["metadata"] = {"confidence": new_confidence}
            
        return self.client.update(memory_id, **update_data)

# Usage example
kb = KnowledgeBase(client, "software_engineering")

# Add knowledge
knowledge = kb.add_knowledge(
    "Python list comprehensions are more efficient than traditional loops for most operations",
    category="performance",
    source="Python Performance Documentation",
    confidence=0.9
)
print("Knowledge added:", knowledge)

# Query knowledge
answers = kb.query_knowledge(
    "How to optimize Python code performance?",
    category="performance"
)
print("Knowledge search results:", answers)
```

### 🔍 Advanced Search Dashboard

```python
class SearchDashboard:
    def __init__(self, client):
        self.client = client
    
    def comprehensive_search(self, query, user_context=None):
        """Perform comprehensive search across all dimensions"""
        
        results = {
            "query": query,
            "timestamp": datetime.now().isoformat(),
            "searches": {}
        }
        
        # Basic search
        results["searches"]["basic"] = self.client.search(
            query=query,
            version="v2",
            limit=10
        )
        
        # User-specific search
        if user_context:
            results["searches"]["user_specific"] = self.client.search(
                query=query,
                user_id=user_context.get("user_id"),
                version="v2",
                limit=10
            )
            
            # Agent-specific search
            if user_context.get("agent_id"):
                results["searches"]["agent_specific"] = self.client.search(
                    query=query,
                    agent_id=user_context["agent_id"],
                    version="v2",
                    limit=10
                )
        
        # High-confidence search
        results["searches"]["high_confidence"] = self.client.search(
            query=query,
            version="v2",
            threshold=0.8,
            limit=5
        )
        
        # Recent memories search
        results["searches"]["recent"] = self.client.search(
            query=query,
            version="v2",
            filters={
                "metadata.timestamp": {
                    "gte": (datetime.now().replace(hour=0, minute=0, second=0)).isoformat()
                }
            },
            limit=10
        )
        
        return results
    
    def search_analytics(self, search_results):
        """Generate analytics for search results"""
        analytics = {
            "total_searches": len(search_results["searches"]),
            "search_types": list(search_results["searches"].keys()),
            "result_counts": {},
            "average_scores": {},
            "top_categories": {}
        }
        
        for search_type, search_result in search_results["searches"].items():
            results = search_result.get("results", [])
            analytics["result_counts"][search_type] = len(results)
            
            if results:
                avg_score = sum(r.get("score", 0) for r in results) / len(results)
                analytics["average_scores"][search_type] = avg_score
        
        return analytics

# Usage example
dashboard = SearchDashboard(client)

# Comprehensive search
search_results = dashboard.comprehensive_search(
    "machine learning best practices",
    user_context={
        "user_id": "data_scientist",
        "agent_id": "ml_assistant"
    }
)

# Get analytics
analytics = dashboard.search_analytics(search_results)
print("Search Dashboard Results:")
print(f"Total searches performed: {analytics['total_searches']}")
print(f"Search types: {', '.join(analytics['search_types'])}")
print(f"Result counts: {analytics['result_counts']}")
print(f"Average scores: {analytics['average_scores']}")
```

---

## 🎯 Summary

This comprehensive guide demonstrates the full power of the Mem0 Python SDK:

### ✅ **Core Features Covered:**
- **Cloud & Local Memory**: Both deployment options
- **Advanced Search**: Semantic, filtered, threshold-based
- **Batch Operations**: Efficient bulk updates/deletions  
- **Entity Management**: User, agent, session handling
- **Export & Analytics**: Data export and insights
- **Real-time Feedback**: Memory quality improvement

### 🚀 **Advanced Patterns:**
- **Semantic Clustering**: Group related memories
- **Multi-modal Search**: Text, image, audio content
- **AI Assistant Integration**: Personalized experiences
- **Knowledge Management**: Structured information systems
- **Search Analytics**: Performance insights

### 💡 **Key Benefits:**
- **Scalable Memory**: Cloud infrastructure
- **Intelligent Search**: AI-powered semantic matching
- **Flexible Filtering**: Complex query capabilities
- **Production Ready**: Batch operations & analytics
- **Easy Integration**: Simple Python API

---

*This guide covers all major functionalities of the Mem0 Python SDK. For the latest features and updates, visit [Mem0 Documentation](https://docs.mem0.ai).*