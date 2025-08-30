# Image Analysis Agent Example

This is a **ready-to-run** example of an AI agent specialized for **object detection and image analysis** using the REPLICATE tool through MCP (Model Context Protocol).

## 🎯 What This Example Does

This agent is specifically designed to:
- Analyze images for object detection
- Use the REPLICATE.run tool with object detection models
- Provide structured responses with confidence scores and bounding boxes
- Display results in a user-friendly format with markdown tables and annotated images

## 🚀 Quick Start

### 1. Set up environment variables
Create a `.env` file in this directory:
```bash
# Required API keys
ACI_API_KEY="your_aci_api_key_here"
GOOGLE_API_KEY="your_gemini_api_key_here"
```

### 2. Install dependencies
```bash
# Make sure you have the required packages installed
pip install python-dotenv fastapi uvicorn camel-ai rich pydantic
```

### 3. Run the agent
```bash
cd example_run
python image_analysis_agent.py
```

The server will start on `http://localhost:8001` (note the different port from the main playground).

### 4. Test the agent
You can test it using curl or any HTTP client:
```bash
curl -X POST "http://localhost:8001/chat" \
     -H "Content-Type: application/json" \
     -d '{"content": "Find the cars in this image: https://example.com/street.jpg"}'
```

Or use the React frontend from the main project by changing the backend URL to `localhost:8001`.

## 🔧 How It Works

### Agent Behavior
The agent is configured with a specialized system prompt that makes it:
1. **Extract image URLs and queries** from user messages
2. **Automatically call REPLICATE.run** with proper parameters
3. **Format responses** with:
   - Natural language summary
   - Markdown table of detected objects
   - Annotated result images

### Configuration
- Uses `create_config.py` to generate MCP configuration
- Connects to ACI.dev's MCP server with REPLICATE tools
- Configured for object detection workflows

### Example Interactions
**User:** "Find the people in this image: https://example.com/crowd.jpg"

**Agent Response:**
1. Calls REPLICATE.run with `{"image": "https://example.com/crowd.jpg", "query": "people"}`
2. Returns formatted analysis with detected persons, confidence scores, and bounding boxes
3. Shows annotated image with detection boxes

## 🔌 Integration with Main Project

This example can be used alongside the main MCP Agent Playground:
- Runs on port **8001** (main project uses 8000)
- Uses the same frontend by changing the API endpoint
- Demonstrates specialized agent configuration

## 📝 Key Files

- `image_analysis_agent.py` - Main FastAPI server with specialized image analysis logic
- `create_config.py` - MCP configuration generator for REPLICATE tools
- `config.json` - Generated MCP server configuration (created automatically)

## 🎨 Customization

To modify this agent:
1. Edit the `system_message_content` in `image_analysis_agent.py`
2. Adjust the tool calling logic in the chat endpoint
3. Modify response formatting as needed

This example serves as a template for creating specialized agents with specific tool integrations! 