# CAMEL AI Playground Setup Guide

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Git (for cloning the repository)

## Quick Setup

### Option 1: Automated Setup (Recommended)
```bash
chmod +x setup.sh
./setup.sh
```

### Option 2: Manual Setup
```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Create necessary directories
mkdir -p conversation_history role_play_history task_history
```

## Environment Configuration

### API Key Setup
1. Copy the environment template:
```bash
# The .env file should contain:
PRIMARY_CAMEL_PROVIDER="OPENAI"
OPENAI_API_KEY="your_actual_openai_key"
ANTHROPIC_API_KEY="your_actual_anthropic_key"
GEMINI_API_KEY="your_actual_gemini_key"
OPENROUTER_API_KEY="your_actual_openrouter_key"
```

2. **Important**: Replace placeholder values with your actual API keys
3. The `PRIMARY_CAMEL_PROVIDER` determines the default provider selection

### Obtaining API Keys

#### OpenAI
1. Visit [OpenAI API](https://platform.openai.com/api-keys)
2. Create an account and generate an API key
3. Models supported: `gpt-3.5-turbo`, `gpt-4`

#### Anthropic
1. Visit [Anthropic Console](https://console.anthropic.com/)
2. Create an account and generate an API key
3. Models supported: `claude-2`

#### Google Gemini
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create an API key
3. Models supported: `gemini-pro`

#### OpenRouter
1. Visit [OpenRouter](https://openrouter.ai/keys)
2. Create an account and generate an API key
3. Access to multiple models including: `google/gemini-flash-1.5`

## Running the Application

### Start the Application
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Run Streamlit app
streamlit run Home.py
```

### Access the Application
- Open your browser to `http://localhost:8501`
- Configure API keys through the sidebar on the Home page
- Navigate between features using the sidebar menu

## Project Structure Explanation

### Core Files
- **`Home.py`**: Main entry point with API key management
- **`requirements.txt`**: Python dependencies specification
- **`setup.sh`**: Automated setup script for Unix systems

### Pages Directory
- **`01_Chat_Agents.py`**: Single-agent chat interface
- **`02_Role_Playing.py`**: Multi-agent role-playing scenarios
- **`03_Task_Automation.py`**: Sequential task execution with progress tracking
- **`04_Visualization.py`**: Analytics and data visualization

### Data Directories
- **`conversation_history/`**: JSON files of single-agent conversations
- **`role_play_history/`**: JSON files of multi-agent sessions
- **`task_history/`**: JSON files of automated task executions

## Feature Guide

### 1. Chat Agents
**Purpose**: Interactive chat with single AI agents
**Key Features**:
- Custom role and personality definition
- Provider and model selection
- Conversation history saving
- Real-time chat interface

### 2. Role Playing
**Purpose**: Multi-agent conversations with defined roles
**Key Features**:
- Two-agent setup (AI Assistant + User Proxy)
- Custom role descriptions for both agents
- Task-based conversation initiation
- Session management and history

### 3. Task Automation
**Purpose**: Sequential task execution with monitoring
**Key Features**:
- Task queue management
- Progress tracking with status indicators
- Flexible model specification (`provider:model_name`)
- Results export and analysis

### 4. Visualization
**Purpose**: Analytics and insights from all interactions
**Key Features**:
- Conversation pattern analysis
- Model performance comparisons
- Interactive charts and graphs
- Data export in multiple formats

## Troubleshooting

### Common Issues

#### 1. Import Errors
```bash
# Error: ModuleNotFoundError: No module named 'camel'
# Solution: Ensure virtual environment is activated and dependencies installed
source venv/bin/activate
pip install -r requirements.txt
```

#### 2. API Key Errors
```bash
# Error: API key not set or invalid
# Solution: Check .env file and ensure keys are valid
# Test keys using the Home page configuration panel
```

#### 3. Model Creation Failures
```bash
# Error: Failed to create model instance
# Solutions:
# 1. Verify model name spelling (case-sensitive)
# 2. Ensure provider supports the specified model
# 3. Check API key validity for the selected provider
```

#### 4. Streamlit Issues
```bash
# Error: Port already in use
streamlit run Home.py --server.port 8502

# Error: Session state issues
# Solution: Clear browser cache or use incognito mode
```

### Debugging Tips

1. **Enable Detailed Logging**:
```python
# All pages have logging configured
# Check terminal output for detailed error messages
```

2. **Check API Key Status**:
- Use the Home page sidebar to verify API key configuration
- Green checkmarks indicate properly configured keys

3. **Verify Model Names**:
- Refer to `REPOSITORY_INDEX.md` for supported model names
- Use exact spelling as specified by providers

## Development Setup

### Code Structure
The application follows a modular structure with shared patterns:

1. **Session State Management**: Each page initializes required session variables
2. **Model Creation**: Standardized factory pattern for all providers
3. **Error Handling**: Consistent error messaging and logging
4. **Data Persistence**: JSON-based storage with timestamps

### Adding New Features
1. Create new page file in `pages/` directory
2. Follow the established patterns for session state and model creation
3. Implement data persistence if needed
4. Update navigation in `Home.py`

### Testing
```bash
# Test basic functionality
streamlit run Home.py

# Navigate through all pages to ensure proper initialization
# Test with at least one configured API key
```

## Security Considerations

1. **API Key Security**:
   - Never commit `.env` files to version control
   - Use environment variables in production
   - Rotate API keys regularly

2. **Data Privacy**:
   - Conversation histories are stored locally
   - No data is sent to third parties beyond AI providers
   - Review and clean history files periodically

## Performance Tips

1. **Model Selection**:
   - Use `gpt-3.5-turbo` for faster responses
   - Use `gpt-4` for more complex tasks
   - Consider cost implications of different models

2. **Large Conversations**:
   - Long conversations may hit token limits
   - Use the "Clear Conversation" feature periodically
   - Monitor response times for performance

## Contributing

1. Fork the repository
2. Create a feature branch
3. Follow the established code patterns
4. Test thoroughly with multiple providers
5. Submit a pull request

For questions or issues, refer to the project's GitHub repository or create an issue. 