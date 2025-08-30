"""
CAMEL AI Prompt Templates

This package contains specialized prompts for CAMEL AI agents:
- Planner Prompt: Instructions for code analysis and planning
- Writer Prompt: Guidelines for technical content generation
"""

from .planner_prompt import PLANNER_PROMPT
from .writer_prompt import WRITER_PROMPT

__all__ = [
    'PLANNER_PROMPT',
    'WRITER_PROMPT'
] 