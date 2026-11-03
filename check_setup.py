import sys
import requests
from PIL import Image
from dotenv import load_dotenv
import os

load_dotenv()
print("Python:", sys.version)
print("Ollama host:", os.getenv("OLLAMA_HOST", "http://localhost:11434"))
try:
    r = requests.get(os.getenv("OLLAMA_HOST", "http://localhost:11434").rstrip("/") + "/api/tags", timeout=10)
    r.raise_for_status()
    print("Ollama: connected")
    print("Models:", [m.get("name") for m in r.json().get("models", [])])
except Exception as e:
    print("Ollama check failed:", type(e).__name__, e)

for package in ["streamlit", "pandas", "openpyxl", "docx", "plotly", "mcp"]:
    try:
        mod = __import__(package)
        print(package, "OK")
    except Exception as e:
        print(package, "MISSING/ERROR:", e)
