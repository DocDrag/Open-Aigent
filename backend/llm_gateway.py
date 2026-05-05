import os
import requests
from typing import Generator

class OllamaClient:
    """Direct Ollama API client. No LangChain, no bloat."""

    def __init__(self, model_name: str = "llama3", base_url: str = None):
        self.model_name = model_name
        self.base_url = base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

    def chat_stream(self, prompt: str, system_prompt: str = "") -> Generator[str, None, None]:
        """Stream tokens directly from Ollama's /api/generate endpoint."""
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "system": system_prompt,
            "stream": True
        }
        try:
            with requests.post(url, json=payload, stream=True, timeout=300) as resp:
                resp.raise_for_status()
                for line in resp.iter_lines():
                    if line:
                        import json
                        data = json.loads(line)
                        token = data.get("response", "")
                        if token:
                            yield token
                        if data.get("done", False):
                            break
        except requests.exceptions.ConnectionError:
            yield "[ERROR: Cannot connect to Ollama. Is it running?]"
        except Exception as e:
            yield f"[ERROR: {str(e)}]"

    @staticmethod
    def fetch_models(base_url: str = None) -> list:
        """Fetch available models from Ollama."""
        url = base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        try:
            resp = requests.get(f"{url}/api/tags", timeout=3)
            if resp.status_code == 200:
                models = resp.json().get("models", [])
                return [m["name"] for m in models]
            return []
        except Exception as e:
            print(f"Ollama connection error: {e}")
            return []
