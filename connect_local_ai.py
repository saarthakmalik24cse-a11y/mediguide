"""Download and verify a local model before selecting it for MediGuide."""
import os
from pathlib import Path
import shutil
import subprocess
import requests
from dotenv import set_key

ROOT = Path(__file__).resolve().parent
MODEL = "qwen3:4b"
BASE = "http://127.0.0.1:11434/v1"


def main():
    executable = shutil.which("ollama")
    fallback = Path(os.environ.get("LOCALAPPDATA", "")) / "Programs/Ollama/ollama.exe"
    if not executable and fallback.is_file():
        executable = str(fallback)
    if not executable:
        print("Install Ollama for Windows from https://ollama.com/download/windows")
        print("Open Ollama once, then run connect_local_ai.bat again. No API key needed.")
        return 1
    try:
        with requests.Session() as session:
            session.trust_env = False
            installed = session.get("http://127.0.0.1:11434/api/tags", timeout=5)
            installed.raise_for_status()
            if not any(model["name"] == MODEL for model in installed.json()["models"]):
                print("Downloading qwen3:4b (about 2.5 GB). No API charges.", flush=True)
                subprocess.run([executable, "pull", MODEL], check=True)
            print("Testing local generation; first load may take a few minutes.", flush=True)
            response = session.post(BASE + "/chat/completions", json={
                "model": MODEL, "messages": [{"role": "user", "content": "Reply only OK."}],
                "max_tokens": 512}, timeout=300)
            response.raise_for_status()
            answer = response.json()["choices"][0]["message"]["content"]
            if not isinstance(answer, str) or not answer.strip():
                raise ValueError("Local model returned no text")
        for name, value in {"LLM_PROVIDER": "openai-compatible", "LLM_BASE_URL": BASE,
                            "LLM_MODEL": MODEL, "LLM_API_KEY": "ollama"}.items():
            set_key(str(ROOT / ".env"), name, value)
        print("Local connection verified and saved. Restart MediGuide. Keep Ollama running.")
        return 0
    except (requests.RequestException, subprocess.CalledProcessError, ValueError, KeyError, IndexError):
        print("Local setup failed; settings not changed. Check Ollama is running and model download completed.")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
