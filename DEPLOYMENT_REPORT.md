# Deployment Audit Report

## Startup Command

Expected:

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Configured in:

- `railway.json`
- `Procfile`

## Environment Variables

Required:

- `DATABASE_URL`
- `OPENAI_API_KEY`

Also referenced:

- `META_AD_LIBRARY_ACCESS_TOKEN` for Meta ad-library crawling.

## Platform Readiness

- Railway Ready? YES
- Render Ready? YES
- Vercel Backend Ready? NO

## Missing Files

Before this audit, the following deployment files were missing:

- `requirements.txt`
- `railway.json`
- `Procfile`
- `.gitignore`

After this audit, no required deployment metadata files are missing.

## Notes

- FastAPI app object exists at `app.main:app`.
- Verification import passed for `app.main:app`.
- `/health` route is registered.
- Local `.env` contains `DATABASE_URL` and `OPENAI_API_KEY` keys. Values were not printed.
- The project expects a PostgreSQL-compatible `DATABASE_URL`.
- The app serves HTML templates from `app/templates`, so `jinja2` is included.
- Playwright is included because `app/crawlers/playwright_crawler.py` imports it. Production images may also need browser installation during build if that crawler is used at runtime.
- `app/db/database.py` loads a local absolute `.env` path, but platform-provided environment variables still satisfy `DATABASE_URL` when set by Railway or Render.

## Recommended Deployment Architecture

Use Railway or Render for the FastAPI backend with managed PostgreSQL/Supabase as the database. Keep Vercel for a separate frontend only; this repository is a Python backend and is not structured as a Vercel serverless backend.
