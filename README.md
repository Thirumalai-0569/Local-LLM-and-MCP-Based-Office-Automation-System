# Local-LLM-and-MCP-Based-Office-Automation-System

A beginner-friendly local office automation project using Streamlit, Ollama, Python, Excel, Word, Plotly, and MCP.

## Features
- Local AI chat through Ollama
- Screenshot analysis using a vision-language model
- Read, summarize, and update Excel workbooks
- Read and create Word documents
- Dynamic charts from uploaded Excel files
- Local MCP stdio server exposing Excel and Word tools

## 1. Requirements
- Windows 10/11
- Python 3.10+ recommended
- Ollama installed and running
- Internet connection only for downloading Python packages and models

## 2. Create virtual environment (CMD)
```cmd
cd path\to\Local-LLM-and-MCP-Based-Office-Automation-System
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 3. Configure environment
Copy `.env.example` to `.env`. You can use:
```env
OLLAMA_HOST=http://localhost:11434
OLLAMA_CHAT_MODEL=qwen2.5:1.5b
OLLAMA_VISION_MODEL=qwen3-vl:2b
OLLAMA_TIMEOUT=600
```

## 4. Download models
```cmd
ollama pull qwen2.5:1.5b
ollama pull qwen3-vl:2b
ollama list
```
The vision model needs more memory than the small text model. If it is too slow or fails to load, check available RAM/VRAM and use a compatible smaller vision model supported by your Ollama installation.

## 5. Check setup
```cmd
python check_setup.py
```

## 6. Run application
```cmd
streamlit run app.py
```
Open the local URL Streamlit prints, usually http://localhost:8501.

## 7. MCP server
The MCP server is `mcp_server/server.py` and uses stdio transport. The Streamlit MCP tab starts it as a child process and lists its tools. Keep standard output reserved for MCP protocol messages; do not add print debugging to the server.

To start it manually for an MCP-compatible client, configure:
- Command: the Python executable from your project virtual environment
- Arguments: `-m mcp_server.server`
- Working directory: the project root

## Troubleshooting
- **Cannot connect to Ollama:** open Ollama, then run `ollama list`.
- **Model not found:** run the relevant `ollama pull` command and verify with `ollama list`.
- **Vision timeout:** use a smaller screenshot, check system memory, and allow more time for first model load.
- **Empty vision response:** this project prints response metadata and raw response details rather than silently returning an empty answer.
- **MCP import error:** activate the virtual environment and run `pip install -r requirements.txt`.
- **MCP connection error:** run `python -m mcp_server.server` only through an MCP client using stdio; it is not a normal web server.

## Project structure
```text
Local-LLM-and-MCP-Based-Office-Automation-System/
├── app.py
├── requirements.txt
├── .env.example
├── check_setup.py
├── modules/
│   ├── ai_chat.py
│   ├── vision_ai.py
│   ├── office_assistant.py
│   ├── dynamic_dashboard.py
│   └── mcp_client.py
├── mcp_server/
│   ├── server.py
│   ├── excel_tools.py
│   └── word_tools.py
├── uploads/
└── output/
    ├── excel/
    └── word/
```

## Notes
- The project does not send files to a cloud AI service. AI requests go to the local Ollama server configured in `.env`.
- Excel and Word file operations are local.
- Always keep backups of important workbooks before editing.
