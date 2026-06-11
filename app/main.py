import logging
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request

from app.db.database import SessionLocal
from app.models.company import Company
from app.models.alert import Alert
from app.api.company_routes import router as company_router
from app.api.dashboard_routes import router as dashboard_router

logger = logging.getLogger(__name__)
BASE_DIR = Path(__file__).resolve().parent
TEMPLATE_DIR = BASE_DIR / "templates"

app = FastAPI(
    title="WATCHDOG",
    description="Competitor Intelligence Agent",
    version="1.0"
)

app.include_router(company_router)
app.include_router(dashboard_router)

templates = Jinja2Templates(
    directory=str(TEMPLATE_DIR)
)


@app.get("/", response_class=HTMLResponse)
def home():
    return HTMLResponse("<h1>WATCHDOG LIVE</h1>")


@app.get("/health")
def health():

    return {
        "status": "healthy"
    }
