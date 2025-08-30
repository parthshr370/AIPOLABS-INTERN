import os
from dotenv import load_dotenv

load_dotenv()

def check_api_keys():
    """Check if API keys are properly set"""
    print("🔍 Checking API Keys...")
    print("=" * 40)
    
    # Check OpenAI API Key
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key and openai_key != "your_openai_api_key_here":
        print(f"✅ OPENAI_API_KEY: {openai_key[:10]}...{openai_key[-5:]}")
    else:
        print("❌ OPENAI_API_KEY: Missing or placeholder")
    
    print("\n🔍 Checking ACI Agent API Keys...")
    print("-" * 40)
    
    # Check ACI API Keys
    agent_keys = [
        "SEARCH_GENIUS_API_KEY",
        "WEB_CRAWLER_API_KEY", 
        "RESEARCHER_API_KEY",
        "SOCIAL_API_KEY",
        "SLACK_MANAGER_API_KEY",
        "HR_SALES_API_KEY",
        "MARKETING_API_KEY",
        "CONTENT_KING_API_KEY",
        "CODE_NINJA_API_KEY",
        "MEMORY_API_KEY",
        "DOCUMENT_MASTER_API_KEY",
        "CRYPTO_API_KEY",
        "VISUAL_ALCHEMIST_API_KEY"
    ]
    
    valid_keys = 0
    for key_name in agent_keys:
        key_value = os.getenv(key_name)
        if key_value and len(key_value) > 10:
            print(f"✅ {key_name}: {key_value[:8]}...")
            valid_keys += 1
        else:
            print(f"❌ {key_name}: Missing")
    
    print("\n" + "=" * 40)
    print(f"📊 Valid Keys: {valid_keys}/{len(agent_keys)}")
    
    if valid_keys == len(agent_keys) and openai_key:
        print("🎉 All keys are set!")
        return True
    else:
        print("⚠️  Some keys are missing")
        return False

def test_simple_agent():
    """Test a simple agent without tools"""
    try:
        from camel.models import ModelFactory
        from camel.types import ModelPlatformType
        
        openai_key = os.getenv("OPENAI_API_KEY")
        if not openai_key or openai_key == "your_openai_api_key_here":
            print("❌ Cannot test: Invalid OpenAI API key")
            return False
            
        print("\n🧪 Testing OpenAI Model...")
        
        model = ModelFactory.create(
            model_platform=ModelPlatformType.OPENAI,
            model_type="gpt-3.5-turbo",
            api_key=openai_key,
            model_config_dict={"temperature": 0.7, "max_tokens": 100}
        )
        
        print("✅ Model created successfully")
        return True
        
    except Exception as e:
        print(f"❌ Model test failed: {e}")
        return False

if __name__ == "__main__":
    print("🔧 ACI Agent Swarm - API Key Checker")
    print("=" * 50)
    
    # Check if keys are set
    keys_ok = check_api_keys()
    
    # Test model if keys are OK
    if keys_ok:
        model_ok = test_simple_agent()
        
        if model_ok:
            print("\n🎯 Ready to run agents!")
            print("Run: python main.py")
        else:
            print("\n⚠️  Model test failed - check your OpenAI API key")
    else:
        print("\n⚠️  Please check your .env file")
    
    print("\n💡 Tip: Get a valid OpenAI API key from:")
    print("   https://platform.openai.com/api-keys")