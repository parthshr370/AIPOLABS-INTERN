"""
Pydantic Schema for Cookbook Intent & Style

This module defines a streamlined and more informative Pydantic schema 
for capturing the style, structure, and intent of a cookbook.
"""

from pydantic import BaseModel, Field
from typing import List, Optional

class StyleGuide(BaseModel):
    """
    A comprehensive guide that captures the style, intent, and structure for the cookbook.
    This single JSON object will guide all subsequent agents.
    """

    # --- Core Intent & Metadata ---
    title: Optional[str] = Field(None, description="The main title of the cookbook.")
    core_intent_summary: str = Field(..., description="A one-sentence summary of the cookbook's main goal and purpose.")
    target_audience: str = Field(..., description="A description of the ideal reader for this cookbook.")
    technology_stack: List[str] = Field(default_factory=list, description="A list of key technologies, libraries, or frameworks covered.")
    difficulty_level: Optional[str] = Field(None, description="Estimated difficulty (e.g., 'Beginner', 'Intermediate', 'Advanced').")


    # --- Writing Style & Voice ---
    tone: str = Field(..., description="The overall tone of the content (e.g., 'formal', 'conversational', 'humorous').")
    verbosity_level: str = Field("concise", description="The desired verbosity ('concise' or 'detailed').")
    content_density: str = Field("scan-friendly", description="The density of the content ('scan-friendly' or 'in-depth').")
    brevity_policy: str = Field(..., description="A specific instruction on how to handle conciseness (e.g., 'Omit needless words').")
    formality_level: int = Field(..., description="A score from 1 (very informal) to 10 (very formal).")
    humor_level: int = Field(..., description="A score from 1 (no humor) to 10 (very humorous).")
    technical_depth: Optional[int] = Field(None, description="A score from 1 (surface-level) to 10 (very deep).")
    personality_adjectives: List[str] = Field(default_factory=list, description="A list of adjectives describing the desired writing personality (e.g., 'playful', 'authoritative').")

    # --- Structure & Formatting ---
    organization_pattern: str = Field(..., description="The structural pattern of the cookbook (e.g., 'problem-solution', 'step-by-step-tutorial', 'reference-guide').")
    section_length_guideline: str = Field(..., description="Guideline for how long each section should be (e.g., 'short', 'medium', 'long').")
    example_usage: str = Field(..., description="How code examples are used (e.g., 'minimal and illustrative', 'comprehensive and production-ready').")

    # --- Formatting & Elements (from Example Cookbook) ---
    formatting_preferences: List[str] = Field(..., description="List of key formatting choices (e.g., ['numbered-lists', 'bold-for-emphasis', 'blockquotes-for-tips']).")
    emoji_usage_policy: str = Field(..., description="Policy on using emojis (e.g., 'none', 'in-headings-only', 'sparingly-in-text').")
    includes_diagrams: bool = Field(..., description="Whether diagrams or visual aids are a key feature of the example style.")

    # --- Agent Control Parameters ---
    planner_instructions: List[str] = Field(..., description="Specific instructions for the Planner Agent based on the inferred style.")
    writer_instructions: List[str] = Field(..., description="Specific instructions for the Writer Agent based on the inferred style.")
    assembler_instructions: List[str] = Field(..., description="Specific instructions for the Assembler Agent based on the inferred style.")