# MCP Agent Playground

A minimal full-stack template for experimenting with **MCP / ACI.dev tools** (or any other agent framework) through a clean React chat interface.

- **Backend** – `FastAPI` + `uvicorn`, powered by [camel-ai](https://github.com/camel-ai) and the `MCPToolkit`.  Lives in `backend/agent_server.py`.
- **Frontend** – React app (in `frontend/`) that speaks JSON over HTTP to the backend.

---

## ✨  Features

1. Chat UI with markdown rendering, image previews and streaming indicator.
2. Automatically lists the tools returned by `GET /tools`.
3. Sidebar with sample prompts you can customise in seconds.
4. Ships with a working demo agent (image analysis) – runs out-of-the-box after you add API keys.
5. Zero vendor-lock-in: swap in your own tools, models or framework by editing **one** Python file.

---

## 🏃‍♂️  Quick Start

### 1.  Clone & enter the project
```bash
git clone <your-fork-url> mcp-agent-playground
cd mcp-agent-playground
```

### 2.  Backend (FastAPI)
```bash
# create & activate venv (optional but recommended)
python -m venv venv
source venv/bin/activate               # Windows: venv\Scripts\activate

pip install -r requirements.txt        # or install packages individually

# required environment variables
export ACI_API_KEY="your_aci_key"
export GOOGLE_API_KEY="your_gemini_key"

# generate config.json (also runs automatically inside the server)
python backend/create_config.py

# run the server from the project root
cd backend
python agent_server.py
```

Endpoints exposed:
- **POST** `/chat`  `{ "content": "Hello agent" }` – returns `{ response, executed_tools }`
- **GET**  `/tools` returns `{ tools: [ { name, description } ] }`
- **WebSocket** `/ws` for real-time streams (the React client uses HTTP by default).

### 3.  Frontend (React)
```bash
cd frontend
npm install            # or yarn
npm start              # opens http://localhost:3000
```
If your backend is not on `localhost:8000` you can change the URLs in `src/components/Chat.js` & `ToolList.js` or add a proxy in `frontend/package.json`.

---

## 🎯  Ready-to-Run Example: Image Analysis Agent

For a **complete working example**, check out the `example_run/` directory which contains a specialized image analysis agent that's ready to use:

```bash
cd example_run
# Copy env.example to .env and add your API keys
cp env.example .env
# Edit .env with your ACI_API_KEY and GOOGLE_API_KEY

# Run the specialized image analysis agent
python image_analysis_agent.py
```

This example demonstrates:
- **Specialized agent behavior** for object detection
- **REPLICATE tool integration** through MCP
- **Structured response formatting** with confidence scores and bounding boxes
- **Ready-to-use configuration** for image analysis workflows

The example runs on port `8001` and can be used with the same React frontend by changing the API endpoint.

See `example_run/README.md` for detailed instructions and customization options.

---

## 🔌  Plug in your own tools / framework
1. Open `backend/agent_server.py`.
2. Replace or extend the logic that builds `mcp_toolkit = MCPToolkit(...)` and the `system_message_content`.
3. Ensure your tools are returned from `mcp_toolkit.get_tools()` **or** supply a list manually.
4. Restart the server – the UI will automatically show the new tools.

---

## 🖌️  Customising the UI
File | Purpose
---- | -------
`frontend/src/components/ProjectInfo.js` | Logo, title & sample prompts
`frontend/src/components/Chat.js`       | Greeting, placeholder text
`frontend/src/components/ToolList.css`  | Styling for the tool list

---

## 🗂️  Repository layout
```
backend/agent_server.py ← FastAPI app (replaceable)
backend/create_config.py← generates config.json for MCP apps
backend/config.json     ← created at runtime (kept in git-ignore if desired)
example_run/            ← Ready-to-run image analysis agent example
├─ image_analysis_agent.py ← Specialized agent for object detection
├─ create_config.py     ← MCP config for REPLICATE tools
├─ env.example          ← Environment variables template
└─ README.md            ← Example-specific documentation
frontend/               ← React codebase
└─ src/components/…     ← UI pieces (Chat, ToolList, etc.)
```

---

## 📄  License
MIT.  Use, modify, distribute – have fun building autonomous agents!
