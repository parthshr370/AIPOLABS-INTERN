# CAMEL AI Playground - Repository Index

## Project Overview
A Streamlit web application for experimenting with CAMEL (Communicative Agents for "Mind" Exploration of Large Language Model Society) AI agents. The application provides interfaces for chat agents, role-playing scenarios, task automation, and visualization.

## Directory Structure
```
camel_playground/
├── Home.py                     # Main entry point, API key management
├── requirements.txt            # Python dependencies (CAMEL AI, Streamlit, etc.)
├── setup.sh                    # Automated setup script
├── README.md                   # Project documentation
├── pages/                      # Streamlit page modules
│   ├── 01_Chat_Agents.py      # Single agent chat interface
│   ├── 02_Role_Playing.py     # Multi-agent role-playing scenarios
│   ├── 03_Task_Automation.py  # Automated task execution
│   └── 04_Visualization.py    # Analytics and data visualization
├── conversation_history/       # Saved single-agent conversations (JSON)
├── role_play_history/         # Multi-agent scenario data (JSON)
├── task_history/              # Task execution records (JSON)
└── .env                       # Environment variables (API keys)
```

## Core Dependencies
- **camel-ai==0.2.16**: Main CAMEL framework for agent creation
- **streamlit>=1.28.0**: Web application framework
- **plotly>=5.18.0**: Interactive visualizations
- **python-dotenv>=1.0.0**: Environment variable management
- **openai>=1.3.0, anthropic>=0.3.11**: LLM API clients

## Code Architecture

### 1. Main Application (`Home.py`)
**Purpose**: Entry point with API key management and navigation
**Key Components**:
- Multi-provider API key management (OpenAI, Anthropic, Gemini, OpenRouter)
- Primary provider selection and storage
- Navigation cards to different features
- Environment variable handling with `.env` file management

**Key Functions**:
```python
def get_primary_provider_index()  # Determines default provider
def main()                        # Main application logic
```

### 2. Chat Agents (`pages/01_Chat_Agents.py`)
**Purpose**: Single agent chat interface with customizable roles
**Key Components**:
- Agent creation with provider/model selection
- Real-time chat interface
- Conversation history management
- Message persistence in JSON format

**Key Functions**:
```python
def create_agent(provider_name, model_name, role, role_description, agent_identifier)
def save_conversation(messages, role, provider, model_name)
def initialize_session_state()
```

**Agent Creation Pattern**:
```python
# Common pattern across all pages
model_instance = ModelFactory.create(
    model_platform=platform_to_pass,
    model_type=model_spec_to_pass,
    api_key=os.getenv(api_key_env_var),
    model_config_dict=model_config
)
agent = ChatAgent(system_message=f"You are a {role}. {role_description}", model=model_instance)
```

### 3. Role Playing (`pages/02_Role_Playing.py`)
**Purpose**: Multi-agent conversations with different roles
**Key Components**:
- Two-agent role-playing setup (AI Assistant + User Proxy)
- Custom role definitions and descriptions
- Conversation initiation and management
- Session history tracking

**Key Imports**:
```python
from camel.societies import RolePlaying
from camel.types import TaskType
```

### 4. Task Automation (`pages/03_Task_Automation.py`)
**Purpose**: Automated task execution with progress tracking
**Key Components**:
- Task definition and queue management
- Sequential task execution
- Progress monitoring and status tracking
- Results saving and export

**Unique Features**:
- Flexible model specification (prefix-based: `provider:model_name`)
- Task status management (`pending`, `running`, `completed`, `failed`)
- Real-time progress updates

### 5. Visualization (`pages/04_Visualization.py`)
**Purpose**: Analytics and data visualization for all interactions
**Key Components**:
- Data loading from history directories
- Statistical analysis of conversations, role-playing, and tasks
- Interactive charts using Plotly and Matplotlib
- Data export functionality (CSV, JSON, Excel)

**Analytics Features**:
- Message count trends over time
- Average message lengths by model
- Conversation duration analysis
- Task completion rates

## Common Code Patterns

### 1. Session State Management
All pages follow a consistent pattern for Streamlit session state:
```python
def initialize_session_state():
    if 'key' not in st.session_state:
        st.session_state.key = default_value
```

### 2. Model Creation
Standard model creation across all pages:
```python
# Provider determination
if provider_lower == "openai":
    platform_to_pass = ModelPlatformType.OPENAI
    api_key_env_var = "OPENAI_API_KEY"
# ... other providers

# Model instance creation
model_instance = ModelFactory.create(
    model_platform=platform_to_pass,
    model_type=model_spec_to_pass,
    api_key=os.getenv(api_key_env_var),
    model_config_dict=model_config
)
```

### 3. Error Handling
Consistent error handling with logging:
```python
try:
    # Model/agent creation
except ValueError as ve:
    st.error(f"Configuration error: {str(ve)}")
    logging.error(f"ValueError: {str(ve)}", exc_info=True)
except Exception as e:
    st.error(f"Unexpected error: {str(e)}")
    logging.error(f"Exception: {str(e)}", exc_info=True)
```

### 4. Data Persistence
JSON-based data storage pattern:
```python
save_dir = Path("history_directory")
save_dir.mkdir(exist_ok=True)
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
filename = save_dir / f"data_{timestamp}.json"
with open(filename, 'w') as f:
    json.dump(data, f, indent=2)
```

## Model Support

### Supported Providers
1. **OpenAI**: `gpt-3.5-turbo`, `gpt-4`
2. **Anthropic**: `claude-2`
3. **Gemini**: `gemini-pro`
4. **OpenRouter**: Various models via `google/gemini-flash-1.5`

### Model Type Mapping
```python
# Short names to ModelType enums
ModelType.GPT_4           # "gpt-4"
ModelType.GPT_35_TURBO    # "gpt-3.5-turbo"
ModelType.CLAUDE_2        # "claude-2"
```

## Environment Configuration

### Required Environment Variables
```bash
# Primary provider (determines default selection)
PRIMARY_CAMEL_PROVIDER="OPENAI"

# API Keys
OPENAI_API_KEY="your_openai_key"
ANTHROPIC_API_KEY="your_anthropic_key"
GEMINI_API_KEY="your_gemini_key"
OPENROUTER_API_KEY="your_openrouter_key"
```

## Setup and Deployment

### Automated Setup
```bash
chmod +x setup.sh
./setup.sh
```

### Manual Setup
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
mkdir -p conversation_history role_play_history task_history
streamlit run Home.py
```

## Key Features

### 1. API Key Management
- Secure storage in `.env` file
- Multi-provider support
- Primary provider selection
- Real-time status indicators

### 2. Agent Customization
- Custom roles and descriptions
- Provider-specific model selection
- Configurable parameters (word limits, etc.)

### 3. Data Export
- Conversation history in JSON
- Analytics export (CSV, Excel, JSON)
- Structured data with timestamps

### 4. Visualization
- Interactive charts with Plotly
- Statistical analysis
- Trend monitoring
- Export capabilities

## Extension Points

### Adding New Providers
1. Update provider mappings in each page
2. Add environment variable handling
3. Update ModelPlatformType enum usage
4. Add default model configurations

### Adding New Features
1. Create new page in `pages/` directory
2. Follow session state initialization pattern
3. Implement model creation pattern
4. Add data persistence if needed

## Troubleshooting

### Common Issues
1. **API Key Errors**: Ensure keys are set in `.env` and provider is selected
2. **Model Creation Failures**: Check model name spelling and provider compatibility
3. **Import Errors**: Verify CAMEL AI version compatibility (0.2.16)
4. **Session State Issues**: Clear browser cache or restart Streamlit

### Logging
All pages use Python logging with INFO level for debugging model creation and agent interactions. 