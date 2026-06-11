from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request

from app.db.database import SessionLocal
from app.models.company import Company
from app.models.alert import Alert
from app.api.company_routes import router as company_router
from app.api.dashboard_routes import router as dashboard_router

app = FastAPI(
    title="WATCHDOG",
    description="Competitor Intelligence Agent",
    version="1.0"
)

app.include_router(company_router)
app.include_router(dashboard_router)

templates = Jinja2Templates(
    directory="app/templates"
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
            "index.html",
            {
                "request": request,
                "companies": companies,
                "alerts": alerts
            }
        )

    finally:
        db.close()


@app.get("/health")
def health():

    return {
        "status": "healthy"
    }