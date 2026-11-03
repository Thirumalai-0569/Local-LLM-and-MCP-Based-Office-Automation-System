import os
import io
import base64
import requests
from PIL import Image, UnidentifiedImageError
from dotenv import load_dotenv

load_dotenv()
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434").rstrip("/")
VISION_MODEL = os.getenv("OLLAMA_VISION_MODEL", "qwen3-vl:2b")
TIMEOUT = int(os.getenv("OLLAMA_TIMEOUT", "600"))

def check_vision_model():
    try:
        r = requests.get(f"{OLLAMA_HOST}/api/tags", timeout=15)
        r.raise_for_status()
        names = [m.get("name", "") for m in r.json().get("models", [])]
        found = any(n == VISION_MODEL or n.startswith(VISION_MODEL + ":") for n in names)
        if not found:
            return False, f"Model {VISION_MODEL} not found. Installed models: {names}"
        return True, f"Connected. Vision model available: {VISION_MODEL}"
    except requests.exceptions.ConnectionError:
        return False, "Cannot connect to Ollama. Start Ollama first."
    except Exception as e:
        return False, f"Ollama check failed: {type(e).__name__}: {e}"

def _image_to_base64(uploaded_file):
    if isinstance(uploaded_file, bytes):
        raw = uploaded_file
    elif isinstance(uploaded_file, str):
        with open(uploaded_file, "rb") as f:
            raw = f.read()
    elif hasattr(uploaded_file, "getvalue"):
        raw = uploaded_file.getvalue()
    elif hasattr(uploaded_file, "read"):
        if hasattr(uploaded_file, "seek"):
            uploaded_file.seek(0)
        raw = uploaded_file.read()
    else:
        raise ValueError("Unsupported image input. Pass a file uploader, bytes, or file path.")
    if not raw:
        raise ValueError("The uploaded image is empty.")
    try:
        image = Image.open(io.BytesIO(raw)).convert("RGB")
    except (UnidentifiedImageError, OSError) as e:
        raise ValueError(f"Cannot open image. Use a valid PNG/JPG/WebP file. Details: {e}")
    image.thumbnail((1024, 1024))
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG", quality=85, optimize=True)
    return base64.b64encode(buffer.getvalue()).decode("utf-8")

def analyze_image(uploaded_file, question=None):
    """Analyze an uploaded image using Ollama's /api/chat vision input."""
    try:
        ready, status = check_vision_model()
        if not ready:
            return f"Vision setup problem: {status}"
        image_b64 = _image_to_base64(uploaded_file)
        prompt = (question or "").strip() or (
            "Describe this image. Read any clearly visible text and explain "
            "important interface elements, warnings, or errors. If text is unclear, say so."
        )
        payload = {
            "model": VISION_MODEL,
            "messages": [{"role": "user", "content": prompt, "images": [image_b64]}],
            "stream": False,
            "keep_alive": "10m",
            "options": {"temperature": 0.2, "num_predict": 300}
        }
        response = requests.post(
            f"{OLLAMA_HOST}/api/chat", json=payload, timeout=(20, TIMEOUT)
        )
        response.raise_for_status()
        data = response.json()
        message = data.get("message") or {}
        answer = message.get("content", "")
        if isinstance(answer, str) and answer.strip():
            return answer.strip()
        return (
            "Ollama returned a response but no answer text was present.\n\n"
            f"Model: {data.get('model')}\n"
            f"Done: {data.get('done')}\n"
            f"Done reason: {data.get('done_reason')}\n"
            f"Response: {data}"
        )
    except FileNotFoundError as e:
        return f"Image file not found: {e}"
    except ValueError as e:
        return f"Image input error: {e}"
    except requests.exceptions.ReadTimeout:
        return f"Vision model timed out after {TIMEOUT} seconds. Try a smaller image or check system memory."
    except requests.exceptions.ConnectionError:
        return "Cannot connect to Ollama. Start Ollama and retry."
    except requests.exceptions.HTTPError as e:
        detail = e.response.text if e.response is not None else ""
        return f"Ollama HTTP error: {e}\n{detail}"
    except requests.exceptions.RequestException as e:
        return f"Ollama network error: {e}"
    except Exception as e:
        return f"Vision error: {type(e).__name__}: {e}"

analyze_screenshot = analyze_image
