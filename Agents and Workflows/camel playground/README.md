# 🐫 CAMEL AI Playground

An interactive web application for experimenting with CAMEL (Communicative Agents for "Mind" Exploration of Large Language Model Society) AI agents. This playground provides an intuitive interface for testing different agent configurations, role-playing scenarios, and automated tasks using the latest CAMEL AI framework.

## ✨ Features

- **💬 Chat Agents**: Create and interact with AI agents with customizable roles and personalities
- **🎭 Role Playing**: Set up scenarios with multiple agents in different roles
- **🎯 Task Automation**: Define and execute sequences of tasks with progress tracking
- **📊 Visualization**: Analyze interaction patterns and performance metrics
- **🔧 Multiple Model Support**: Compatible with OpenAI GPT models, Anthropic Claude, Google Gemini, and OpenRouter
- **🔐 Secure API Key Management**: Built-in secure storage and management of API keys
- **💾 Data Export**: Export analytics and conversation history in various formats
- **🎨 Modern UI**: Beautiful, responsive interface with gradient designs and animations

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Git (for cloning the repository)

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/yourusername/camel-playground.git
cd camel-playground
```

2. **Create and activate a virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Run the integration test:**
```bash
python test_camel_integration.py
```

5. **Start the application:**
```bash
streamlit run Home.py
```

6. **Open your browser** and navigate to `http://localhost:8501`

## 🔑 API Key Setup

The application supports multiple AI providers. You can configure API keys through the web interface:

1. **Navigate to the Home page**
2. **Use the sidebar to select your preferred provider**
3. **Enter your API key and save**

### Supported Providers

#### OpenAI
- **Models**: `gpt-4.1`, `gpt-4.1-mini`, `gpt-4o`, `gpt-4o-mini`, `o3`, `o4-mini`, `gpt-4`, `gpt-3.5-turbo`
- **Latest**: `gpt-4.1` (strong coding/reasoning), `o3` (advanced reasoning for complex tasks)
- **Get API Key**: [OpenAI Platform](https://platform.openai.com/api-keys)

#### Anthropic
- **Models**: `claude-opus-4-20250514`, `claude-sonnet-4-20250514`, `claude-3-7-sonnet-20250219`, `claude-3-5-haiku-20241022`
- **Latest**: `claude-opus-4-20250514` (most capable, advanced coding/agentic), `claude-sonnet-4-20250514` (high-performance, balanced)
- **Get API Key**: [Anthropic Console](https://console.anthropic.com/)

#### Google Gemini
- **Models**: `gemini-2.5-pro-preview-05-06`, `gemini-2.5-flash-preview-05-20`, `gemini-2.0-flash`, `gemini-1.5-pro`, `gemini-1.5-flash`
- **Latest**: `gemini-2.5-pro-preview-05-06` (most advanced, reasoning, multimodal), `gemini-2.5-flash-preview-05-20` (fast, cost-efficient)
- **Get API Key**: [Google AI Studio](https://makersuite.google.com/app/apikey)

#### OpenRouter
- **Models**: Access to multiple models including `google/gemini-flash-1.5`
- **Get API Key**: [OpenRouter](https://openrouter.ai/keys)

## 📁 Project Structure

```
camel_playground/
├── Home.py                    # Main application entry point
├── pages/                     # Streamlit pages
│   ├── 01_Chat_Agents.py     # Single agent chat interface
│   ├── 02_Role_Playing.py    # Multi-agent role-playing scenarios
│   ├── 03_Task_Automation.py # Task automation and execution
│   └── 04_Visualization.py   # Analytics and data visualization
├── conversation_history/      # Saved chat conversations
├── role_play_history/        # Role-playing session data
├── task_history/             # Task execution records
├── requirements.txt          # Python dependencies
├── test_camel_integration.py # Integration test script
├── SETUP_GUIDE.md           # Detailed setup instructions
└── README.md                # This file
```

## 🎯 Usage Guide

### 1. Chat Agents
**Purpose**: Interactive chat with single AI agents

**Features**:
- Custom role and personality definition
- Provider and model selection
- Real-time conversation
- Message history and export

**Getting Started**:
1. Navigate to "Chat Agents" from the home page
2. Configure your agent in the sidebar
3. Set the role (e.g., "Python Expert", "Creative Writer")
4. Start chatting!

### 2. Role Playing
**Purpose**: Multi-agent conversations with defined roles

**Features**:
- Two-agent setup with custom roles
- Task-based conversation initiation
- Session management and history
- Configurable response length

**Example Scenarios**:
- Python Programmer + Stock Trader
- Teacher + Student
- Product Manager + Developer

### 3. Task Automation
**Purpose**: Sequential task execution with monitoring

**Features**:
- Task queue management
- Progress tracking with status indicators
- Flexible model specification
- Results analysis and export

### 4. Visualization
**Purpose**: Analytics and insights from interactions

**Features**:
- Conversation pattern analysis
- Model performance comparisons
- Interactive charts and graphs
- Data export capabilities

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
# Primary provider (optional)
PRIMARY_CAMEL_PROVIDER="OPENAI"

# API Keys (add the ones you plan to use)
OPENAI_API_KEY="your_openai_key_here"
ANTHROPIC_API_KEY="your_anthropic_key_here"
GEMINI_API_KEY="your_gemini_key_here"
OPENROUTER_API_KEY="your_openrouter_key_here"
```

### Model Configuration

Each agent can be configured with:
- **Custom roles and descriptions**
- **Specific model selection**
- **Temperature and token limits**
- **Provider-specific parameters**

## 🧪 Testing

Run the comprehensive integration test:

```bash
python test_camel_integration.py
```

This test verifies:
- ✅ All imports work correctly
- ✅ CAMEL AI version compatibility
- ✅ Model types and configurations
- ✅ Message creation functionality
- ✅ Directory structure setup

## 🛠️ Development

### Adding New Features

The application follows a modular structure:

1. **Session State Management**: Each page initializes required session variables
2. **Model Creation**: Standardized factory pattern for all providers
3. **Error Handling**: Consistent error messaging and logging
4. **Data Persistence**: JSON-based storage with timestamps

### Code Structure

```python
# Example: Adding a new provider
def create_agent(provider_name: str, model_name: str, role: str, role_description: str):
    if provider_lower == "new_provider":
        api_key = os.getenv("NEW_PROVIDER_API_KEY")
        model_instance = ModelFactory.create(
            model_platform=ModelPlatformType.NEW_PROVIDER,
            model_type=model_name,
            model_config_dict=config_dict,
            api_key=api_key
        )
    # ... rest of the logic
```

## 🐛 Troubleshooting

### Common Issues

#### Import Errors
```bash
# Error: ModuleNotFoundError: No module named 'camel'
# Solution: Ensure virtual environment is activated and dependencies installed
source venv/bin/activate
pip install -r requirements.txt
```

#### API Key Errors
```bash
# Error: API key not set or invalid
# Solution: Check API keys in the Home page configuration panel
```

#### Model Creation Failures
- Verify model name spelling (case-sensitive)
- Ensure provider supports the specified model
- Check API key validity for the selected provider

#### Streamlit Issues
```bash
# Port already in use
streamlit run Home.py --server.port 8502

# Session state issues - clear browser cache or use incognito mode
```

### Debug Mode

Enable detailed logging by checking the terminal output where you run the Streamlit app. All pages have comprehensive logging configured.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Development Setup

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `python test_camel_integration.py`
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **CAMEL AI Team** for their groundbreaking work on communicative agents
- **Streamlit Team** for their excellent web application framework
- **OpenAI, Anthropic, and Google** for their powerful language models

## 📞 Support

For questions, suggestions, or issues:

1. Check the [SETUP_GUIDE.md](SETUP_GUIDE.md) for detailed instructions
2. Run the integration test: `python test_camel_integration.py`
3. Open an issue in the GitHub repository
4. Contact the maintainers

## 🔄 Version History

- **v2.0.0** - Updated to CAMEL AI 0.2.57+, improved UI, enhanced error handling
- **v1.0.0** - Initial release with basic chat, role-playing, and task automation

---

**Built with ❤️ using CAMEL AI and Streamlit**

*Ready to explore the future of AI agents? Start your journey now!* 🚀