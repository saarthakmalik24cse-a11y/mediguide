"""Interactive local setup: credentials never appear in chat or command arguments."""
from getpass import getpass
from pathlib import Path
import sys
import warnings
import re
import requests
from dotenv import set_key

ROOT = Path(__file__).resolve().parent
MODEL = "gpt-5.4"


def prompt_key() -> str:
    """Use a masked native field on Windows so normal Ctrl+V works."""
    if sys.platform == "win32":
        import tkinter as tk
        from tkinter import simpledialog
        root = tk.Tk()
        root.withdraw()
        try:
            root.attributes("-topmost", True)
            value = simpledialog.askstring(
                "MediGuide - Connect AI",
                "Copy the full secret key using the Copy button.\n"
                "Click below and press Ctrl+V, then OK.\n"
                "The key stays hidden. Cancel makes no changes.",
                show="*", parent=root,
            )
            return (value or "").strip()
        finally:
            root.destroy()
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        return getpass("Paste API key (hidden), then press Enter: ").strip()


def validate_key(key: str) -> None:
    if not re.fullmatch(r"sk-[A-Za-z0-9_-]{20,}", key):
        raise ValueError("The pasted text is not a complete API key, or contains hidden characters. Copy the full key again, reopen this launcher, and paste once into the popup. Do not paste a Tracking ID or quotes. Nothing saved.")


def safe_error(response, key: str) -> str:
    """Show provider diagnostics without echoing credentials or raw HTML."""
    try:
        error = response.json().get("error", {})
        message = error.get("message", "No structured error detail returned.")
        code = error.get("code") or error.get("type") or "unknown"
        detail = f"{code}: {message}"
    except (ValueError, AttributeError, TypeError):
        content_type = getattr(response, "headers", {}).get("content-type", "unknown")
        detail = "Non-JSON response (" + str(content_type) + "). This does not identify a billing or model error. Try again on a different network, such as a phone hotspot; do not disable security software."
    detail = detail.replace(key, "[REDACTED]") if key else detail
    detail = re.sub(r"sk-[A-Za-z0-9_-]+", "[REDACTED]", detail)
    detail = " ".join(detail.split())
    detail = "".join(c for c in detail if c.isprintable())
    return detail[:700]


def verify(key: str) -> None:
    validate_key(key)
    response = requests.post("https://api.openai.com/v1/chat/completions",
                             headers={"Authorization": "Bearer " + key},
                             json={"model": MODEL, "messages": [{"role": "user", "content": "Reply with OK."}]}, timeout=90)
    if response.status_code == 401:
        raise ValueError("Key was rejected. Check your OpenAI API key.")
    if response.status_code == 429:
        raise ValueError("API returned HTTP 429. " + safe_error(response, key) + "\nIf insufficient_quota: check API billing/credits. If rate_limit_exceeded: wait and retry. Settings were not saved.")
    if not response.ok:
        raise ValueError(f"API returned HTTP {response.status_code}. " + safe_error(response, key) + "\nSettings were not saved.")
    content = response.json()["choices"][0]["message"]["content"]
    if not isinstance(content, str) or not content.strip():
        raise ValueError("Connection returned no answer; settings were not saved.")


def main() -> int:
    print("MediGuide connected AI setup")
    print("Selected model: " + MODEL + ". One small API test will use your API credits.")
    print("The app sends retrieved evidence and recent messages to OpenAI. Use synthetic data.")
    print("Create your API key at https://platform.openai.com/api-keys")
    print("Your key will be stored in this project's Git-ignored .env file (not encrypted).")
    if not sys.stdin.isatty():
        print("Open connect_ai.bat in a terminal to enter the key privately.")
        return 1
    try:
        print("Enter your key in the private popup window (Ctrl+V).")
        key = prompt_key()
        if not key or any(c.isspace() for c in key):
            print("No valid key entered; nothing changed.")
            return 1
        print("Testing connection...")
        verify(key)
        for name, value in {"LLM_PROVIDER": "openai-compatible", "LLM_BASE_URL": "https://api.openai.com/v1",
                            "LLM_MODEL": MODEL, "LLM_API_KEY": key}.items():
            set_key(str(ROOT / ".env"), name, value)
        print("Connection verified. Settings saved. Restart any old MediGuide server before continuing.")
        return 0
    except ValueError as exc:
        print(str(exc))
    except (requests.RequestException, KeyError, IndexError):
        print("Connection test failed. Check internet access and API account settings. Nothing saved.")
    except (KeyboardInterrupt, EOFError, Warning):
        print("Setup cancelled; hidden key input unavailable or interrupted.")
    except OSError:
        print("Could not save configuration. Check folder permissions.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
