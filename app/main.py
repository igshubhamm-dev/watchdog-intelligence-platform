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
def home(request: Request):

    db = SessionLocal()

    try:

        companies = (
            db.query(Company)
            .order_by(Company.id.desc())
            .all()
        )

        alerts = (
            db.query(Alert)
            .order_by(Alert.id.desc())
            .limit(20)
            .all()
        )

        return templates.TemplateResponse(
            name="index.html",
            context={
                "request": request,
                "companies": companies,
                "alerts": alerts
            }
        )

    except Exception:
        logger.exception("Homepage render failed")
        return templates.TemplateResponse(
            name="index.html",
            context={
                "request": request,
                "companies": [],
                "alerts": []
            }
        )

    finally:
        db.close()


@app.get("/health")
def health():

    return {
        "status": "healthy"
    }
