import sys
import os

# Ensure the backend root is on sys.path so `app` package resolves correctly
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app  # noqa: F401 — Vercel picks up the `app` ASGI object
