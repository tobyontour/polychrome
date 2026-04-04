from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .api import router as api_router
from .html import router as html_router

BASE_DIR = Path(__file__).resolve().parent
static_files = StaticFiles(directory=BASE_DIR / "../static")

app = FastAPI(title="polychrome api", version="0.1.0")
app.mount("/static", static_files, name="static")
app.include_router(api_router)
app.include_router(html_router)
