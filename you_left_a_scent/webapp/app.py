"""FastAPI application assembly."""

from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .routes import router


app = FastAPI(title="You Left a Scent", version="1.0.0")
app.include_router(router)

_STATIC_DIR = Path(__file__).resolve().parent.parent / "web_static"
app.mount("/", StaticFiles(directory=_STATIC_DIR, html=True), name="site")
