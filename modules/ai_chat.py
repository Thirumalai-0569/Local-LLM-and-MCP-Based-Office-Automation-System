import os
import requests
from dotenv import load_dotenv

load_dotenv()
HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434").rstrip("/")
MODEL = os.getenv("OLLAMA_CHAT_MODEL", "qwen2.5:1.5b")
TIMEOUT = int(os.getenv("OLLAMA_TIMEOUT", "600"))

def ask_local_llm(history):
    """Send Ollama-format role/content history to the local chat endpoint."""
    try:
        messages = [
            {"role": m["role"], "content": m["content"]}
            for m in history if m.get("role") in ("user", "assistant", "system")
        ]
        if not messages:
            return "Please enter a message."
        response = requests.post(
            f"{HOST}/api/chat",
            json={"model": MODEL, "messages": messages, "stream": False,
                  "keep_alive": "10m", "options": {"temperature": 0.3, "num_predict": 400}},
            timeout=(15, TIMEOUT)
        )
        response.raise_for_status()
        data = response.json()
        answer = (data.get("message") or {}).get("content", "").strip()
        return answer or f"Ollama returned no text. Response: {data}"
    except requests.exceptions.ConnectionError:
        return "Cannot connect to Ollama. Open Ollama and check http://localhost:11434."
    except requests.exceptions.Timeout:
        return "Ollama request timed out. Try again or use a smaller model."
    except requests.exceptions.HTTPError as e:
        detail = e.response.text if e.response is not None else ""
        return f"Ollama API error: {e}\n{detail}"
    except Exception as e:
        return f"Chat error: {type(e).__name__}: {e}"
