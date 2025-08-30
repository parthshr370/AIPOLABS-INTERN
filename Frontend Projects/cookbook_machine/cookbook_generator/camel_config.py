"""
CAMEL AI Configuration for Cookbook Generator

This module contains configuration settings and utility functions
for the CAMEL AI multi-agent system.
"""

import os
from typing import Dict, Any
from camel.types import ModelPlatformType, ModelType

class CAMELConfig:
    """Configuration class for CAMEL AI agents"""
    
    # Agent-specific model configurations
    PLANNER_CONFIG = {
        "model_platform": ModelPlatformType.GEMINI,
        "model_type": "gemini-2.5-flash",
        "temperature": 0.0,
        "max_tokens": 60000,
    }
    
    WRITER_CONFIG = {
        "model_platform": ModelPlatformType.GEMINI,
        "model_type": "gemini-2.5-flash",
        "temperature": 0.2,
        "max_tokens": 60000,
    }
    
    ASSEMBLER_CONFIG = {
        "model_platform": ModelPlatformType.GEMINI,
        "model_type": "gemini-2.5-flash",
        "temperature": 0.1,
        "max_tokens": 60000,
    }

    STYLE_DESIGNER_CONFIG = {
        "model_platform": ModelPlatformType.GEMINI,
        "model_type": "gemini-2.5-flash",
        "temperature": 0.1,
        "max_tokens": 60000,
    }
    
    @classmethod
    def get_model_config(cls, agent_type: str) -> Dict[str, Any]:
        """Get model configuration for a specific agent type"""
        config_map = {
            "planner": cls.PLANNER_CONFIG,
            "writer": cls.WRITER_CONFIG,
            "assembler": cls.ASSEMBLER_CONFIG,
            "style_designer": cls.STYLE_DESIGNER_CONFIG,
        }
        
        base_config = config_map.get(agent_type, cls.PLANNER_CONFIG).copy()
        
        # Override with environment variables if available
        if os.getenv("CAMEL_MODEL_TEMPERATURE"):
            base_config["temperature"] = float(os.getenv("CAMEL_MODEL_TEMPERATURE"))
        
        if os.getenv("CAMEL_MODEL_MAX_TOKENS"):
            base_config["max_tokens"] = int(os.getenv("CAMEL_MODEL_MAX_TOKENS"))
        
        return base_config
    
    @classmethod
    def validate_environment(cls) -> bool:
        """Validate that required environment variables are set"""
        required_vars = []
        
        # Check for Gemini API key (used by all agents now)
        if not os.getenv("GOOGLE_API_KEY"):
            required_vars.append("GOOGLE_API_KEY")

        # (No Anthropic key required when all agents use Gemini)
        
        if required_vars:
            raise ValueError(f"Required environment variables not set: {', '.join(required_vars)}")
        
        return True

# Global configuration instance
camel_config = CAMELConfig() 