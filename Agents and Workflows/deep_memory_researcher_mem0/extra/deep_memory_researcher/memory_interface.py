import warnings
from mem0 import MemoryClient
from rich.console import Console

from config import (
    USER_ID,
    MEM0_API_KEY,
    DEFAULT_SEARCH_LIMIT,
    BULK_RETRIEVAL_LIMIT,
    PROGRESSIVE_THRESHOLDS,
)

warnings.filterwarnings("ignore", category=DeprecationWarning)


class MemoryInterface:
    def __init__(self):
        self.console = Console()
        self.mem0 = MemoryClient(api_key=MEM0_API_KEY)

    def search(self, query, threshold=0.4, limit=None, user_id=None):
        """Basic mem0 search wrapper"""
        if limit is None:
            limit = DEFAULT_SEARCH_LIMIT
        if user_id is None:
            user_id = USER_ID

        try:
            results = self.mem0.search(
                query=query, user_id=user_id, threshold=threshold, limit=limit
            )
            return results if results else []
        except Exception as e:
            self.console.print(f"[red]Search error: {e}[/red]")
            return []

    def get_all(self, user_id=None, limit=None):
        """Bulk memory retrieval"""
        if user_id is None:
            user_id = USER_ID
        if limit is None:
            limit = BULK_RETRIEVAL_LIMIT

        try:
            results = self.mem0.get_all(user_id=user_id, limit=limit)

            if results:
                self.console.print(
                    f"[bold yellow]🔍 SAMPLE MEM0 RESPONSE STRUCTURE:[/bold yellow]"
                )
                sample = results[0] if len(results) > 0 else {}
                self.console.print(
                    f"[dim]Sample memory keys: {list(sample.keys()) if isinstance(sample, dict) else 'Not a dict'}[/dim]"
                )
                if isinstance(sample, dict):
                    self.console.print(
                        f"[dim]Sample content preview: {str(sample)[:200]}...[/dim]"
                    )

            return results if results else []
        except Exception as e:
            self.console.print(f"[red]Get all error: {e}[/red]")
            return []

    def progressive_search(self, query, user_id=None):
        """Search with fallback thresholds [0.5, 0.4, 0.3, 0.2]"""
        if user_id is None:
            user_id = USER_ID

        self.console.print(f"[yellow]🔍 Progressive search: '{query}'[/yellow]")

        for threshold in PROGRESSIVE_THRESHOLDS:
            self.console.print(f"[dim]  Trying threshold {threshold}...[/dim]")
            results = self.search(query, threshold=threshold, user_id=user_id)

            if results:
                self.console.print(
                    f"[green]✓ Found {len(results)} results at threshold {threshold}[/green]"
                )
                return results

        self.console.print("[yellow]  Falling back to broader search...[/yellow]")
        all_memories = self.get_all(user_id=user_id, limit=50)

        filtered = []
        query_lower = query.lower()

        for memory in all_memories:
            memory_content = str(
                memory.get("text", "") + " " + str(memory.get("content", ""))
            ).lower()
            if any(word in memory_content for word in query_lower.split()):
                filtered.append(memory)

        if filtered:
            self.console.print(
                f"[green]✓ Fallback found {len(filtered)} matching memories[/green]"
            )
        else:
            self.console.print(f"[yellow]⚠ No results found for '{query}'[/yellow]")

        return filtered

    def format_memory_content(self, memory):
        """Extract readable content from memory object"""
        if isinstance(memory, dict):
            content = memory.get("memory", "")
            memory_id = memory.get("id", "unknown")
            metadata = memory.get("metadata", {})
            patient_name = metadata.get("patient_name", "")

            if content:
                if patient_name:
                    return f"[Patient: {patient_name}] {content}"
                else:
                    return f"[ID: {memory_id}] {content}"
            else:
                self.console.print(
                    f"[yellow]⚠ No memory content in {memory_id}. Available keys: {list(memory.keys())}[/yellow]"
                )
                return f"[ID: {memory_id}] [No content found]"
        return str(memory)

    def get_memory_ids(self, memories):
        """Extract memory IDs for evidence linking"""
        ids = []
        for memory in memories:
            if isinstance(memory, dict):
                memory_id = memory.get("id", "unknown")
                ids.append(memory_id)
        return ids