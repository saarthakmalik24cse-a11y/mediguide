"""Download official English OCR data locally; run once with network access."""
from pathlib import Path
import requests

if __name__ == "__main__":
    root = Path(__file__).resolve().parent / "data" / "ocr"
    root.mkdir(parents=True, exist_ok=True)
    for filename in ("eng.traineddata", "LICENSE"):
        response = requests.get("https://raw.githubusercontent.com/tesseract-ocr/tessdata_fast/main/" + filename, timeout=30)
        response.raise_for_status()
        (root / filename).write_bytes(response.content)
    print("Official English OCR model and license saved to data/ocr.")
