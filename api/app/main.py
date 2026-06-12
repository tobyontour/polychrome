from pathlib import Path

from fastapi import Depends, FastAPI
from fastapi.staticfiles import StaticFiles
from .routers.api import router as api_router
from .routers.html import router as html_router
from .auth import get_current_user
from .routers.auth import router as auth_router

BASE_DIR = Path(__file__).resolve().parent
static_files = StaticFiles(directory=BASE_DIR / "../static", check_dir=False)

app = FastAPI(title="polychrome api", version="0.1.0")
app.mount("/static", static_files, name="static")
app.include_router(api_router, dependencies=[Depends(get_current_user)])
app.include_router(html_router)
app.include_router(auth_router)
