import os
from dotenv import load_dotenv

load_dotenv()

# API Configuration
USER_ID = "doctor_memory"  # Using same user_id as medical data
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MEM0_API_KEY = os.getenv("MEM0_API_KEY")
MODEL_TYPE = "gemini-1.5-pro-latest"

# System Configuration
# No caching - just simple data flow

# Model Configuration - Import CAMEL types  
from camel.types import ModelType

CHEAP_MODEL_TYPE = ModelType.GEMINI_2_5_FLASH    # For metadata analysis (1M context)
SMART_MODEL_TYPE = ModelType.GEMINI_2_5_PRO      # For research agents (complex reasoning)
MODEL_TEMPERATURE = 0.2
MAX_TOKENS = 40000

# Research process configuration
MAX_RESEARCH_STEPS = 10
MAX_CONTEXT_LENGTH = 16000

# Search Configuration  
DEFAULT_SEARCH_LIMIT = 20
BULK_RETRIEVAL_LIMIT = 1000
PROGRESSIVE_THRESHOLDS = [0.5, 0.4, 0.3, 0.2]
SEARCH_THRESHOLD_PROGRESSION = [0.5, 0.4, 0.3, 0.2]
SEARCH_FALLBACK_QUERY = "medical data"
SEARCH_RESULT_LIMIT = 10

# Research Configuration
CONTEXT_ACCUMULATION_LIMIT = 50000  # Max characters in research context