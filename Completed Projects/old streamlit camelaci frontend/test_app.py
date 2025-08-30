#!/usr/bin/env python3
"""
Simple test script to verify Streamlit app components
"""
import os
import sys
from dotenv import load_dotenv

def test_imports():
    """Test if all required imports work"""
    print("🧪 Testing imports...")
    
    try:
        import streamlit as st
        print("✅ Streamlit imported successfully")
    except ImportError as e:
        print(f"❌ Streamlit import failed: {e}")
        return False
    
    try:
        import nest_asyncio
        print("✅ nest_asyncio imported successfully")
    except ImportError as e:
        print(f"❌ nest_asyncio import failed: {e}")
        return False
    
    try:
        from camel.agents import ChatAgent
        from camel.messages import BaseMessage
        from camel.models import ModelFactory
        from camel.toolkits import MCPToolkit
        from camel.types import ModelPlatformType
        print("✅ CAMEL-AI imports successful")
    except ImportError as e:
        print(f"❌ CAMEL-AI import failed: {e}")
        return False
    
    return True

def test_env_loading():
    """Test environment variable loading"""
    print("\n🧪 Testing environment loading...")
    
    load_dotenv()
    
    google_key = os.getenv("GOOGLE_API_KEY", "")
    aci_key = os.getenv("ACI_API_KEY", "")
    linked_id = os.getenv("LINKED_ACCOUNT_OWNER_ID", "")
    
    print(f"Google API Key: {'✅ Found' if google_key else '❌ Missing'}")
    print(f"ACI API Key: {'✅ Found' if aci_key else '❌ Missing'}")
    print(f"Linked Account ID: {'✅ Found' if linked_id else '❌ Missing'}")
    
    return all([google_key, aci_key, linked_id])

def test_config_creation():
    """Test MCP config creation"""
    print("\n🧪 Testing config creation...")
    
    try:
        import json
        
        # Mock session state
        class MockSessionState:
            def __init__(self):
                self.aci_api_key = os.getenv("ACI_API_KEY", "test_key")
                self.linked_account_id = os.getenv("LINKED_ACCOUNT_OWNER_ID", "test_id")
        
        # Create mock config
        mock_state = MockSessionState()
        
        config = {
            "mcpServers": {
                "aci_apps": {
                    "command": "uvx",
                    "args": [
                        "aci-mcp",
                        "apps-server",
                        "--apps=BRAVE_SEARCH,GITHUB,ARXIV",
                        "--linked-account-owner-id",
                        mock_state.linked_account_id,
                    ],
                    "env": {"ACI_API_KEY": mock_state.aci_api_key},
                }
            }
        }
        
        # Test JSON serialization
        json_str = json.dumps(config, indent=2)
        print("✅ Config creation successful")
        return True
        
    except Exception as e:
        print(f"❌ Config creation failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🐪 CAMEL-AI MCP Frontend - Component Tests\n")
    
    tests = [
        ("Imports", test_imports),
        ("Environment", test_env_loading),
        ("Config Creation", test_config_creation),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    print("\n📊 Test Results:")
    print("=" * 40)
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name:20} {status}")
        if not passed:
            all_passed = False
    
    print("=" * 40)
    
    if all_passed:
        print("🎉 All tests passed! The app should work correctly.")
        print("\n🚀 You can now run: streamlit run streamlit_app.py")
    else:
        print("⚠️  Some tests failed. Please check the issues above.")
        print("\n💡 Common fixes:")
        print("   - Install missing packages: pip install -r requirements.txt")
        print("   - Check your .env file has all required API keys")
        print("   - Ensure CAMEL-AI is properly installed")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 