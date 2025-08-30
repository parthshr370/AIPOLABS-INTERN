# 🐪 CAMEL-AI & ACI.dev MCP Playground

An interactive playground for experimenting with CAMEL-AI agents enhanced by ACI.dev's Model Context Protocol (MCP) tools. Test how AI agents can intelligently use external tools for comprehensive responses.

## Features

- **Interactive Playground**: Experiment with CAMEL-AI agents and ACI.dev MCP tools
- **Tool Visualization**: See all available ACI.dev tools before processing
- **Progress Tracking**: Real-time progress indicators during agent execution
- **Tool Monitoring**: Track which ACI.dev tools are triggered during execution
- **Configurable Settings**: Sidebar configuration for API keys and model parameters
- **Raw Output**: Collapsible detailed output for debugging and learning
- **Auto-Configuration**: Automatically loads settings from environment variables

## Available ACI.dev MCP Tools

The playground connects to ACI.dev's MCP server and provides access to:
- **BRAVE_SEARCH**: Real-time web search via ACI.dev's Brave Search integration
- **GITHUB**: Repository and code search through ACI.dev's GitHub tools
- **ARXIV**: Academic paper search via ACI.dev's arXiv integration

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Environment Configuration

Create a `.env` file in the project directory:

```bash
cp env.example .env
```

Edit the `.env` file with your credentials:

```env
# Google Gemini API Key
GOOGLE_API_KEY="your_google_api_key_here"

# ACI Platform Configuration
ACI_API_KEY="your_aci_api_key_here"
LINKED_ACCOUNT_OWNER_ID="your_linked_account_owner_id_here"
```

### 3. Get Required API Keys

#### Google API Key
1. Go to [Google AI Studio](https://aistudio.google.com/)
2. Create a new API key
3. Copy the key to your `.env` file

#### ACI API Key
1. Visit [ACI Platform](https://platform.aci.dev/apps)
2. Configure your apps and get your API key
3. Set up OAuth flow to get your Linked Account Owner ID
4. Copy both values to your `.env` file

## Usage

### Running the Application

```bash
streamlit run streamlit_app.py
```

The application will open in your browser at `http://localhost:8501`

### Using the Playground

1. **Configuration**: The sidebar will auto-load your environment variables
   - Verify/modify API keys if needed
   - Adjust model settings (temperature, max tokens, model type)
   - All fields must be filled for the playground to work

2. **Experiment**: Enter your question in the text area
   - Example: "search for the best books of 2024"
   - Example: "find recent papers about machine learning on arXiv"
   - Example: "search GitHub for Python web frameworks"

3. **Processing**: Click "🚀 Process Query" to start
   - Watch the progress indicators
   - See available ACI.dev tools being loaded
   - Monitor which tools get triggered by the CAMEL-AI agent

4. **Results**: View the AI agent's response
   - Main response is displayed prominently
   - Triggered ACI.dev tools are highlighted
   - Raw output is available in collapsible section for learning

### Configuration Options

#### Model Settings
- **Model Type**: Choose between Gemini variants
  - `gemini-2.5-pro-preview-05-06` (default)
  - `gemini-1.5-pro`
  - `gemini-1.5-flash`
- **Temperature**: Control response randomness (0.0-1.0)
- **Max Tokens**: Set maximum response length (1000-50000)

#### MCP Configuration
The app automatically configures the MCP server with:
- Command: `uvx aci-mcp apps-server`
- Apps: `BRAVE_SEARCH,GITHUB,ARXIV`
- Your API credentials

## Project Structure

```
camelaci-frontend/
├── streamlit_app.py          # Main Streamlit application
├── camel_mcp_aci.py         # Original CLI version
├── create_config.py         # MCP configuration utility
├── config.json              # Generated MCP configuration
├── requirements.txt         # Python dependencies
├── env.example             # Environment template
├── .env                    # Your environment variables (create this)
└── README.md               # This file
```

## Troubleshooting

### Common Issues

1. **"Please fill in all required fields"**
   - Ensure all API keys are provided in the sidebar
   - Check that your `.env` file is properly formatted

2. **Connection errors**
   - Verify your API keys are valid
   - Check your internet connection
   - Ensure `uvx` and `aci-mcp` are installed

3. **No tools available**
   - Check ACI API key validity
   - Verify linked account owner ID is correct
   - Ensure MCP server is properly configured

### Installation Requirements

Make sure you have:
- Python 3.8+
- `uv` package manager: `pip install uv`
- `aci-mcp` server: Installed via `uvx`

### Debug Mode

Use the "🔍 Raw Output" expander to see:
- Complete response objects
- Tool call details
- Error traces
- Response metadata

## Development

### Running the Original CLI Version

```bash
python camel_mcp_aci.py
```

### Modifying Tool Configuration

Edit the `create_config_from_sidebar()` function in `streamlit_app.py` to:
- Add new tools to the `--apps` parameter
- Modify MCP server settings
- Change command line arguments

## License

This project is part of the CAMEL-AI ecosystem. Please refer to the original project's license terms.

## Support

For issues related to:
- **CAMEL-AI**: Visit [CAMEL-AI GitHub](https://github.com/camel-ai/camel)
- **ACI Platform**: Check [ACI Documentation](https://platform.aci.dev/)
- **This Frontend**: Create an issue in this repository 