#!/usr/bin/env python3
"""
Test script to verify CAMEL AI integration works correctly.
This script tests basic functionality without requiring API keys.
"""

import sys
import os
from pathlib import Path

def test_imports():
    """Test that all required imports work correctly."""
    print("Testing imports...")
    
    try:
        import streamlit as st
        print("✅ Streamlit imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import Streamlit: {e}")
        return False
    
    try:
        from camel.agents import ChatAgent
        from camel.messages import BaseMessage
        from camel.types import ModelType, ModelPlatformType
        from camel.models import ModelFactory
        from camel.configs import ChatGPTConfig, AnthropicConfig, GeminiConfig
        print("✅ CAMEL AI imports successful")
    except ImportError as e:
        print(f"❌ Failed to import CAMEL AI components: {e}")
        return False
    
    try:
        import plotly.graph_objects as go
        import pandas as pd
        import matplotlib.pyplot as plt
        import seaborn as sns
        print("✅ Visualization libraries imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import visualization libraries: {e}")
        return False
    
    return True

def test_camel_version():
    """Test CAMEL AI version and basic functionality."""
    print("\nTesting CAMEL AI version...")
    
    try:
        import camel
        version = camel.__version__
        print(f"✅ CAMEL AI version: {version}")
        
        # Check if version is recent enough
        version_parts = version.split('.')
        major, minor = int(version_parts[0]), int(version_parts[1])
        
        if major == 0 and minor >= 2:
            print("✅ CAMEL AI version is compatible")
            return True
        else:
            print(f"⚠️ CAMEL AI version {version} might be outdated. Recommended: 0.2.57+")
            return True  # Still allow it to work
            
    except Exception as e:
        print(f"❌ Error checking CAMEL AI version: {e}")
        return False

def test_model_types():
    """Test that model types are available."""
    print("\nTesting model types...")
    
    try:
        from camel.types import ModelType, ModelPlatformType
        
        # Test some common model types with correct names
        openai_models = [ModelType.GPT_4, ModelType.GPT_3_5_TURBO, ModelType.GPT_4O]
        platforms = [ModelPlatformType.OPENAI, ModelPlatformType.ANTHROPIC, ModelPlatformType.GEMINI]
        
        print("✅ Model types accessible:")
        for model in openai_models:
            print(f"  - {model}")
        
        print("✅ Platform types accessible:")
        for platform in platforms:
            print(f"  - {platform}")
            
        return True
        
    except Exception as e:
        print(f"❌ Error accessing model types: {e}")
        return False

def test_config_classes():
    """Test that config classes work correctly."""
    print("\nTesting configuration classes...")
    
    try:
        from camel.configs import ChatGPTConfig, AnthropicConfig, GeminiConfig
        
        # Test creating config instances
        openai_config = ChatGPTConfig(temperature=0.7, max_tokens=4096)
        anthropic_config = AnthropicConfig(temperature=0.7, max_tokens=4096)
        gemini_config = GeminiConfig(temperature=0.7, max_tokens=4096)
        
        print("✅ Configuration classes work:")
        print(f"  - OpenAI config: {type(openai_config).__name__}")
        print(f"  - Anthropic config: {type(anthropic_config).__name__}")
        print(f"  - Gemini config: {type(gemini_config).__name__}")
        
        # Test as_dict method
        openai_dict = openai_config.as_dict()
        print(f"  - Config as dict: {list(openai_dict.keys())}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error with configuration classes: {e}")
        return False

def test_message_creation():
    """Test message creation functionality."""
    print("\nTesting message creation...")
    
    try:
        from camel.messages import BaseMessage
        
        # Test creating different types of messages
        user_msg = BaseMessage.make_user_message(role_name="User", content="Hello, world!")
        assistant_msg = BaseMessage.make_assistant_message(role_name="Assistant", content="Hello! How can I help you?")
        
        print("✅ Message creation successful:")
        print(f"  - User message: {user_msg.role_name} - {user_msg.content[:20]}...")
        print(f"  - Assistant message: {assistant_msg.role_name} - {assistant_msg.content[:20]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating messages: {e}")
        return False

def test_directory_structure():
    """Test that required directories exist or can be created."""
    print("\nTesting directory structure...")
    
    required_dirs = ["conversation_history", "role_play_history", "task_history"]
    
    for dir_name in required_dirs:
        dir_path = Path(dir_name)
        try:
            dir_path.mkdir(exist_ok=True)
            print(f"✅ Directory {dir_name} ready")
        except Exception as e:
            print(f"❌ Failed to create directory {dir_name}: {e}")
            return False
    
    return True

def main():
    """Run all tests."""
    print("🐫 CAMEL AI Playground - Integration Test")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_camel_version,
        test_model_types,
        test_config_classes,
        test_message_creation,
        test_directory_structure
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                print(f"❌ Test {test.__name__} failed")
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
    
    print("\n" + "=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The CAMEL AI integration is ready to use.")
        print("\nNext steps:")
        print("1. Set your API keys in the .env file or Home page")
        print("2. Run: streamlit run Home.py")
        print("3. Start experimenting with CAMEL AI agents!")
        return True
    else:
        print("⚠️ Some tests failed. Please check the error messages above.")
        print("You may need to:")
        print("1. Update dependencies: pip install -r requirements.txt")
        print("2. Check your Python environment")
        print("3. Verify CAMEL AI installation")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 