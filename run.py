"""Start TalentVerse from ANY folder:  python run.py"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(HERE)
sys.path.insert(0, HERE)

try:
    import uvicorn
    import fastapi  # noqa: F401
    import pydantic  # noqa: F401
except ImportError:
    print("\nMissing packages. Run this first:\n    python -m pip install -r requirements.txt\n")
    sys.exit(1)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8000"))
    print(f"\nTalentVerse running -> http://127.0.0.1:{port}   (Ctrl+C to stop)\n")
    uvicorn.run("app.main:app", host="127.0.0.1", port=port)
