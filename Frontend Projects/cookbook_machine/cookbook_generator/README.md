# Cookbook Generator - CAMEL AI Multi-Agent System

A sophisticated cookbook generator powered by **CAMEL AI** multi-agent framework, featuring autonomous agents that collaborate to create comprehensive technical documentation from source code.

## 🤖 CAMEL AI Architecture

This application demonstrates a real-world implementation of the CAMEL AI framework with four specialized agents:

- **🎨 Style Designer Agent**: Analyzes an example cookbook to define the style, tone, and structure for the output.
- **🧠 Planner Agent**: Uses Google Gemini 2.0 Flash Exp to analyze user requirements and create structured documentation plans based on the defined style.
- **✍️ Writer Agent**: Uses Anthropic Claude 3.5 Sonnet to draft detailed content for each section, adhering to the style guide.  
- **🔧 Assembler Agent**: Uses Anthropic Claude 3.5 Sonnet to intelligently compile and format the final cookbook, ensuring it matches the target style.

## 🚀 Features

- **Advanced Style & Intent Analysis**: Define cookbook style by providing an example.
- **Multi-Agent Collaboration**: Autonomous agents communicate via CAMEL AI message system
- **Intelligent Planning**: Dynamic analysis of source code and user requirements
- **High-Quality Content**: Advanced AI models for professional documentation
- **Real-time Streaming**: Server-Sent Events for live progress updates
- **Robust Error Handling**: Comprehensive validation and fallback mechanisms

## 📋 Prerequisites

- Python 3.8+
- Google Gemini API key
- Anthropic Claude API key

## 🛠️ Installation

1. **Clone the repository**:
   ```bash
   git clone <your-repo-url>
   cd cookbook_generator
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv camel_env
   source camel_env/bin/activate  # On Windows: camel_env\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up API keys**:
   Create a `.env` file in the root directory:
   ```bash
   GOOGLE_API_KEY=your_google_gemini_api_key_here
   ANTHROPIC_API_KEY=your_anthropic_claude_api_key_here
   ```

   Or export them as environment variables:
   ```bash
   export GOOGLE_API_KEY="your_google_gemini_api_key_here"
   export ANTHROPIC_API_KEY="your_anthropic_claude_api_key_here"
   ```

## 🎯 Getting API Keys

### Google Gemini API Key
1. Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Create a new API key for Gemini models
3. Copy the key for use in your environment

### Anthropic Claude API Key  
1. Visit [Anthropic Console](https://console.anthropic.com/)
2. Create an account and navigate to API Keys
3. Generate a new API key for Claude models
4. Copy the key for use in your environment

## 🏃‍♂️ Usage

1. **Start the Flask application**:
   ```bash
   python app.py
   ```

2. **Access the API**:
   - Server runs on `http://localhost:5000`
   - Main endpoint: `POST /api/generate-cookbook`

3. **API Request Format**:
   ```json
   {
     "user_guidance": "Create a comprehensive guide for this React application",
     "source_code": "// Your source code here...",
     "example_cookbook": "# An example cookbook to copy the style from..."
   }
   ```

4. **Response**: Server-Sent Events stream with real-time updates

## 🧪 Testing

Run the comprehensive test suite:

```bash
python test_camel_agents.py
```

Tests include:
- ✅ Environment validation
- ✅ CAMEL AI imports
- ✅ Configuration system
- ✅ Agent creation
- ✅ Prompt templates

## ⚙️ Configuration

The system uses centralized configuration in `camel_config.py`:

- **Planner Agent**: Gemini 2.0 Flash Exp (Temperature: 0.0, Max Tokens: 50,000)
- **Writer Agent**: Claude 3.5 Sonnet (Temperature: 0.2, Max Tokens: 50,000)  
- **Assembler Agent**: Claude 3.5 Sonnet (Temperature: 0.1, Max Tokens: 50,000)

Override via environment variables:
```bash
export CAMEL_MODEL_TEMPERATURE=0.3
export CAMEL_MODEL_MAX_TOKENS=75000
```

## �� Agent Details

### Style Designer Agent (Gemini 2.5 Pro)
- Analyzes an example cookbook and user guidance.
- Generates a detailed JSON object defining the style, tone, and structure.
- Ensures all subsequent agents adhere to a consistent output style.

### Planner Agent (Gemini 2.0 Flash Exp)
- Analyzes user guidance, source code, and skeleton templates, while following the style guide.
- Generates structured JSON plans with Pydantic validation
- Optimized for analytical and planning tasks

### Writer Agent (Claude 3.5 Sonnet)
- Drafts detailed content for each planned section
- Incorporates code examples and explanations
- Optimized for high-quality content generation

### Assembler Agent (Claude 3.5 Sonnet)  
- Intelligently compiles sections into cohesive documentation
- Ensures consistency and flow across the entire cookbook
- Performs final formatting and optimization

## 📊 Benefits of CAMEL AI Integration

- **Unified Framework**: Single dependency for multi-agent orchestration
- **Advanced Communication**: Sophisticated agent-to-agent messaging
- **Memory Management**: Stateful context preservation across interactions
- **Extensible Architecture**: Easy integration of additional tools and capabilities
- **Production Ready**: Robust error handling and monitoring

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For issues related to:
- **CAMEL AI Framework**: Visit [CAMEL AI Documentation](https://docs.camel-ai.org/)
- **This Implementation**: Open an issue in this repository

---

**Powered by CAMEL AI** 🐫 - The leading multi-agent framework for autonomous AI collaboration 