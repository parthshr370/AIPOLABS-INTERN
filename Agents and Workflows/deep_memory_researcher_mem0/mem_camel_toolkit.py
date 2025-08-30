import time
from typing import Optional, Dict, List, Any, Union
from uuid import uuid4

from camel.memories import ChatHistoryMemory
from camel.memories.context_creators.score_based import (
    ScoreBasedContextCreator,
)
from camel.memories.records import MemoryRecord
from camel.messages import BaseMessage
from camel.storages.key_value_storages.mem0_cloud import Mem0Storage
from camel.toolkits.base import BaseToolkit
from camel.toolkits.function_tool import FunctionTool
from camel.types import ModelType, OpenAIBackendRole, RoleType
from camel.utils import OpenAITokenCounter


class Mem0CloudToolkit(BaseToolkit):
    """A comprehensive toolkit for interacting with Mem0 cloud memory storage.
    
    This toolkit provides a complete interface to Mem0's cloud storage system,
    offering all functionality available in the mem0 Python SDK. It supports
    advanced memory operations including individual memory management, batch
    operations, search with filters, entity management, and export capabilities.
    
    Unlike the standard MemoryToolkit which works with local file-based memory, 
    this toolkit provides cloud-based persistent memory with advanced search 
    capabilities, version control, and comprehensive metadata support.
    
    Args:
        agent_id (str): The agent identifier for memory organization.
        user_id (str): The user identifier for memory organization.
        timeout (Optional[float], optional): Maximum execution time allowed for
            toolkit operations in seconds. If None, no timeout is applied.
            (default: :obj:`None`)
    """

    def __init__(
        self, 
        agent_id: str, 
        user_id: str, 
        timeout: Optional[float] = None
    ):
        super().__init__(timeout=timeout)
        self.agent_id = agent_id
        self.user_id = user_id
        self.memory = self._setup_memory()

    def _setup_memory(self) -> ChatHistoryMemory:
        """Sets up CAMEL's memory components with Mem0 as the backend."""
        storage = Mem0Storage(agent_id=self.agent_id, user_id=self.user_id)
        token_counter = OpenAITokenCounter(ModelType.GPT_4O_MINI)
        context_creator = ScoreBasedContextCreator(
            token_counter=token_counter, token_limit=4096
        )
        return ChatHistoryMemory(
            context_creator=context_creator,
            storage=storage,
            agent_id=self.agent_id,
        )

    def add_memory(
        self, 
        content: Union[str, List[Dict[str, str]]], 
        metadata: Optional[Dict[str, Any]] = None,
        filters: Optional[Dict[str, Any]] = None,
        version: str = "v2",
        output_format: str = "v1.1"
    ) -> str:
        """Adds a new memory record to Mem0 cloud storage.

        Args:
            content (Union[str, List[Dict]]): The information to remember. Can be:
                - A string message
                - A list of message dictionaries with 'role' and 'content' keys
            metadata (dict, optional): Additional metadata to store with the memory.
            filters (dict, optional): Additional filters for memory scoping.
            version (str, optional): API version to use. Defaults to "v2".
            output_format (str, optional): Output format version. Defaults to "v1.1".

        Returns:
            str: Formatted response with memory creation results.
        """
        try:
            # Convert content to messages format if it's a string
            if isinstance(content, str):
                messages = [{"role": "user", "content": content}]
            elif isinstance(content, list):
                messages = content
            else:
                messages = [{"role": "user", "content": str(content)}]
            
            # Use the direct client for advanced features
            result = self.memory._chat_history_block.storage.client.add(
                messages=messages,
                user_id=self.user_id,
                agent_id=self.agent_id,
                metadata=metadata,
                filters=filters,
                version=version,
                output_format=output_format
            )
            return f"Memory added successfully. Result: {str(result)}"
        except Exception as e:
            return f"Error adding memory: {str(e)}"

    def get_memory(self, memory_id: str) -> str:
        """Retrieves a specific memory by ID from Mem0 cloud storage.

        Args:
            memory_id (str): The unique identifier of the memory to retrieve.

        Returns:
            str: Formatted memory data or error message.
        """
        try:
            result = self.memory._chat_history_block.storage.client.get(memory_id)
            return f"Memory retrieved successfully:\n{str(result)}"
        except Exception as e:
            return f"Error retrieving memory {memory_id}: {str(e)}"
    
    def retrieve_memories(
        self, 
        version: str = "v1",
        limit: Optional[int] = None,
        filters: Optional[Dict[str, Any]] = None,
        page: Optional[int] = None,
        page_size: Optional[int] = None
    ) -> str:
        """Retrieves all memories from Mem0 cloud storage with filtering options.

        Args:
            version (str, optional): API version ("v1" or "v2"). Defaults to "v1".
            limit (int, optional): Maximum number of memories to return.
            filters (dict, optional): Additional filters to apply.
            page (int, optional): Page number for pagination (v2 only).
            page_size (int, optional): Page size for pagination (v2 only).

        Returns:
            str: Formatted list of memories.
        """
        try:
            params = {
                "user_id": self.user_id,
                "agent_id": self.agent_id,
            }
            if filters:
                params.update(filters)
            if limit:
                params["limit"] = limit
            if page and page_size:
                params["page"] = page
                params["page_size"] = page_size
                
            result = self.memory._chat_history_block.storage.client.get_all(
                version=version, **params
            )
            return f"Retrieved {len(result) if isinstance(result, list) else 'unknown'} memories:\n{str(result)}"
        except Exception as e:
            return f"Error retrieving memories: {str(e)}"

    def search_memories(
        self, 
        query: str, 
        version: str = "v2",
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 10,
        threshold: Optional[float] = None,
        rerank: bool = True,
        output_format: str = "v1.1"
    ) -> str:
        """Searches for memories in Mem0 cloud storage based on a query.

        This uses Mem0's semantic search with:
        - Vector-based semantic matching
        - Advanced metadata filtering
        - Reranking for better results
        - Threshold-based filtering

        Args:
            query (str): The search term to find relevant memories.
            version (str, optional): API version ("v1" or "v2"). Defaults to "v2".
            filters (dict, optional): Custom filters to apply. If None, uses OR filter
                for user_id and agent_id.
            limit (int, optional): Maximum number of results. Defaults to 10.
            threshold (float, optional): Minimum similarity score threshold.
            rerank (bool, optional): Whether to enable reranking. Defaults to True.
            output_format (str, optional): Output format version. Defaults to "v1.1".

        Returns:
            str: Formatted search results.
        """
        try:
            # Use provided filters or default OR filter
            search_filters = filters or {
                "OR": [
                    {"user_id": self.user_id},
                    {"agent_id": self.agent_id}
                ]
            }
            
            search_params = {
                "version": version,
                "filters": search_filters,
                "output_format": output_format,
                "limit": limit,
                "user_id": self.user_id,
                "agent_id": self.agent_id
            }
            
            if threshold is not None:
                search_params["threshold"] = threshold
            if version == "v2":
                search_params["rerank"] = rerank
                search_params["top_k"] = limit
                
            results = self.memory._chat_history_block.storage.client.search(
                query, **search_params
            )
            return f"Found {len(results) if isinstance(results, list) else 'unknown'} matching memories:\n{str(results)}"
        except Exception as e:
            return f"Search error: {str(e)}"

    def update_memory(
        self, 
        memory_id: str, 
        text: Optional[str] = None, 
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Updates a memory by ID with new text or metadata.

        Args:
            memory_id (str): The unique identifier of the memory to update.
            text (str, optional): New text content for the memory.
            metadata (dict, optional): New metadata for the memory.

        Returns:
            str: Update confirmation or error message.
        """
        try:
            result = self.memory._chat_history_block.storage.client.update(
                memory_id=memory_id,
                text=text,
                metadata=metadata
            )
            return f"Memory {memory_id} updated successfully: {str(result)}"
        except Exception as e:
            return f"Error updating memory {memory_id}: {str(e)}"
    
    def delete_memory(self, memory_id: str) -> str:
        """Deletes a specific memory by ID from Mem0 cloud storage.

        Args:
            memory_id (str): The unique identifier of the memory to delete.

        Returns:
            str: Deletion confirmation or error message.
        """
        try:
            result = self.memory._chat_history_block.storage.client.delete(memory_id)
            return f"Memory {memory_id} deleted successfully: {str(result)}"
        except Exception as e:
            return f"Error deleting memory {memory_id}: {str(e)}"
    
    def delete_memories(
        self, 
        user_id: Optional[str] = None, 
        agent_id: Optional[str] = None,
        app_id: Optional[str] = None,
        run_id: Optional[str] = None
    ) -> str:
        """Deletes all memories from Mem0 cloud storage with optional filtering.

        Args:
            user_id (str, optional): Delete memories for specific user ID.
            agent_id (str, optional): Delete memories for specific agent ID.
            app_id (str, optional): Delete memories for specific app ID.
            run_id (str, optional): Delete memories for specific run ID.

        Returns:
            str: Deletion confirmation message.
        """
        try:
            # If no filters provided, delete for current user and agent
            if not any([user_id, agent_id, app_id, run_id]):
                user_id = self.user_id
                agent_id = self.agent_id
                
            result = self.memory._chat_history_block.storage.client.delete_all(
                user_id=user_id,
                agent_id=agent_id,
                app_id=app_id,
                run_id=run_id
            )
            return f"Memories deleted successfully: {str(result)}"
        except Exception as e:
            return f"Error deleting memories: {str(e)}"

    def get_memory_history(self, memory_id: str) -> str:
        """Retrieves the history of changes for a specific memory.

        Args:
            memory_id (str): The unique identifier of the memory.

        Returns:
            str: Formatted history of memory changes.
        """
        try:
            result = self.memory._chat_history_block.storage.client.history(memory_id)
            return f"Memory history for {memory_id}:\n{str(result)}"
        except Exception as e:
            return f"Error retrieving history for memory {memory_id}: {str(e)}"
    
    def get_users(self) -> str:
        """Retrieves all users, agents, and sessions for which memories exist.

        Returns:
            str: Formatted list of entities.
        """
        try:
            result = self.memory._chat_history_block.storage.client.users()
            return f"Entities with memories:\n{str(result)}"
        except Exception as e:
            return f"Error retrieving entities: {str(e)}"
    
    def delete_users(
        self,
        user_id: Optional[str] = None,
        agent_id: Optional[str] = None, 
        app_id: Optional[str] = None,
        run_id: Optional[str] = None
    ) -> str:
        """Deletes specific entities or all entities if no filters provided.

        Args:
            user_id (str, optional): User ID to delete.
            agent_id (str, optional): Agent ID to delete.
            app_id (str, optional): App ID to delete.
            run_id (str, optional): Run ID to delete.

        Returns:
            str: Deletion confirmation message.
        """
        try:
            result = self.memory._chat_history_block.storage.client.delete_users(
                user_id=user_id,
                agent_id=agent_id,
                app_id=app_id,
                run_id=run_id
            )
            return f"Entities deleted successfully: {str(result)}"
        except Exception as e:
            return f"Error deleting entities: {str(e)}"
    
    def reset_memory(self) -> str:
        """Resets the memory system by deleting all users and memories.

        Returns:
            str: Reset confirmation message.
        """
        try:
            result = self.memory._chat_history_block.storage.client.reset()
            return f"Memory system reset successfully: {str(result)}"
        except Exception as e:
            return f"Error resetting memory system: {str(e)}"
    
    def batch_update_memories(self, memories: List[Dict[str, Any]]) -> str:
        """Batch update multiple memories at once.

        Args:
            memories (List[Dict]): List of memory dictionaries to update.
                Each dict must contain 'memory_id' and 'text' keys.

        Returns:
            str: Batch update confirmation message.
        """
        try:
            result = self.memory._chat_history_block.storage.client.batch_update(memories)
            return f"Batch update completed successfully: {str(result)}"
        except Exception as e:
            return f"Error in batch update: {str(e)}"
    
    def batch_delete_memories(self, memories: List[Dict[str, Any]]) -> str:
        """Batch delete multiple memories at once.

        Args:
            memories (List[Dict]): List of memory dictionaries to delete.
                Each dict must contain 'memory_id' key.

        Returns:
            str: Batch deletion confirmation message.
        """
        try:
            result = self.memory._chat_history_block.storage.client.batch_delete(memories)
            return f"Batch deletion completed successfully: {str(result)}"
        except Exception as e:
            return f"Error in batch deletion: {str(e)}"
    
    def provide_feedback(
        self, 
        memory_id: str, 
        feedback: Optional[str] = None,
        feedback_reason: Optional[str] = None
    ) -> str:
        """Provides feedback on a memory for quality improvement.

        Args:
            memory_id (str): The unique identifier of the memory.
            feedback (str, optional): Feedback type ("POSITIVE", "NEGATIVE", "VERY_NEGATIVE").
            feedback_reason (str, optional): Reason for the feedback.

        Returns:
            str: Feedback submission confirmation.
        """
        try:
            result = self.memory._chat_history_block.storage.client.feedback(
                memory_id=memory_id,
                feedback=feedback,
                feedback_reason=feedback_reason
            )
            return f"Feedback submitted successfully: {str(result)}"
        except Exception as e:
            return f"Error submitting feedback: {str(e)}"
    
    def create_memory_export(self, schema: str, **kwargs) -> str:
        """Creates a memory export with the provided schema.

        Args:
            schema (str): JSON schema defining the export structure.
            **kwargs: Optional filters like user_id, run_id, etc.

        Returns:
            str: Export creation confirmation with request ID.
        """
        try:
            result = self.memory._chat_history_block.storage.client.create_memory_export(
                schema=schema, **kwargs
            )
            return f"Memory export created successfully: {str(result)}"
        except Exception as e:
            return f"Error creating memory export: {str(e)}"
    
    def get_memory_export(self, **kwargs) -> str:
        """Retrieves a memory export.

        Args:
            **kwargs: Filters like user_id to get specific export.

        Returns:
            str: Exported memory data.
        """
        try:
            result = self.memory._chat_history_block.storage.client.get_memory_export(**kwargs)
            return f"Memory export retrieved successfully: {str(result)}"
        except Exception as e:
            return f"Error retrieving memory export: {str(e)}"
    
    def get_memory_summary(self, filters: Optional[Dict[str, Any]] = None) -> str:
        """Gets a summary of memory export.

        Args:
            filters (dict, optional): Optional filters to apply to the summary request.

        Returns:
            str: Memory export summary data.
        """
        try:
            result = self.memory._chat_history_block.storage.client.get_summary(filters=filters)
            return f"Memory summary: {str(result)}"
        except Exception as e:
            return f"Error retrieving memory summary: {str(e)}"

    def get_tools(self) -> list[FunctionTool]:
        """Returns a comprehensive list of FunctionTool objects for the agent.
        
        Returns:
            list[FunctionTool]: Complete list of memory management tools matching
                all functionality available in the mem0 Python SDK.
        """
        return [
            # Core memory operations
            FunctionTool(self.add_memory),
            FunctionTool(self.get_memory),
            FunctionTool(self.retrieve_memories),
            FunctionTool(self.search_memories),
            FunctionTool(self.update_memory),
            FunctionTool(self.delete_memory),
            FunctionTool(self.delete_memories),
            
            # History and tracking
            FunctionTool(self.get_memory_history),
            
            # Entity management
            FunctionTool(self.get_users),
            FunctionTool(self.delete_users),
            
            # System operations
            FunctionTool(self.reset_memory),
            
            # Batch operations
            FunctionTool(self.batch_update_memories),
            FunctionTool(self.batch_delete_memories),
            
            # Quality and feedback
            FunctionTool(self.provide_feedback),
            
            # Export and analytics
            FunctionTool(self.create_memory_export),
            FunctionTool(self.get_memory_export),
            FunctionTool(self.get_memory_summary),
        ]