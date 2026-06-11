# Competitive Intelligence Hardening Report

## Phase 1 Audit

### Duplicate insertion points

- `app/services/alert_service.py`
  - OLD: Always inserted a new alert for every message.
  - NEW: Checks `(company_id, message)` before insert and returns the existing alert.

- `app/services/briefing_service.py`
  - OLD: Always inserted a new briefing for every analysis run.
  - NEW: Upserts by `company_id`; existing briefing is updated.

- `app/services/signal_summary_service.py`
  - OLD: Always inserted a new summary for every `(company_id, signal_type)`.
  - NEW: Upserts by `(company_id, signal_type)`.

- `app/services/job_listing_service.py`
  - OLD: Exact-case title check only; invalid crawler output could be saved.
  - NEW: Validates job title, dedupes per batch, case-insensitive lookup, updates existing URL.

- `app/services/personnel_service.py`
  - OLD: Local blocklist only; no URL/article/customer-story validation and no per-batch normalization.
  - NEW: Shared person-name validation, case-insensitive lookup, role update on existing records.

- `app/services/news_article_service.py`
  - OLD: Only title was checked; duplicate URLs could be inserted.
  - NEW: Validates article title, requires URL, dedupes by title and URL, checks both before insert.

- `app/services/competitor_service.py`
  - OLD: Exact-case competitor-name check only.
  - NEW: Normalizes whitespace, dedupes per batch, case-insensitive lookup.

### Missing uniqueness checks

OLD: SQLAlchemy models had no table-level uniqueness for competitors, jobs, personnel, news, alerts, signal summaries, or briefings.

NEW: Added `UniqueConstraint` definitions in:

- `app/models/competitor.py`: `(company_id, competitor_name)`
- `app/models/personnel.py`: `(company_id, name)`
- `app/models/job_listing.py`: `(company_id, title)`
- `app/models/news_article.py`: `(company_id, title)` and `(company_id, url)`
- `app/models/alert.py`: `(company_id, message)`
- `app/models/signal_summary.py`: `(company_id, signal_type)`
- `app/models/briefing.py`: `(company_id)`

### Poor crawler logic

- `app/crawlers/job_scraper.py`
  - OLD: Any anchor containing role-ish words could become a job, even if the link was navigation/product content.
  - NEW: Requires job URL hints, validates title, normalizes and dedupes output.

- `app/crawlers/personnel_scraper.py`
  - OLD: Passed whole page text to AI, including nav/header/footer/script noise.
  - NEW: Removes noisy tags, validates AI output, dedupes names.

- `app/crawlers/blog_scraper.py`
  - OLD: Basic title/path filtering and silent failures.
  - NEW: Uses shared news validation, normalized URLs, dedupe, logging, retrying HTTP client.

- `app/crawlers/news_scraper.py`
  - OLD: `feedparser.parse(rss_url)` had no HTTP timeout control and could fail unpredictably.
  - NEW: Fetches RSS via timeout/retry HTTP client, handles parser warnings, validates and dedupes entries.

- `app/crawlers/context_graph_builder.py`
  - OLD: Selected links by broad text match, could cross to external pages, repeated raw `requests.get`.
  - NEW: Same-site page discovery, fallback probing through retrying HTTP client, structured logging.

### Bad AI prompts and exception handling

- `app/ai/leadership_analyzer.py`
  - OLD: Prompt did not explicitly reject article titles, customer stories, product names, or page headlines.
  - NEW: Prompt does, and API exceptions return `[]`.

- `app/ai/competitor_analyzer.py`
  - OLD: Prompt could return the company itself or product/category names; API failures bubbled up.
  - NEW: Prompt rejects those outputs and API exceptions return `[]`.

- `app/ai/news_analyzer.py`
  - OLD: API failures aborted pipeline.
  - NEW: API failures return a fallback analysis string.

- `app/ai/briefing_generator.py`
  - OLD: API failures aborted pipeline.
  - NEW: API failures return a fallback briefing string.

### Missing validation layers

OLD: Validation existed only partially in `personnel_service.py` and inside individual crawlers.

NEW: Added `app/services/data_quality.py` with:

- `is_valid_job_title`
- `is_valid_person_name`
- `is_valid_news_article`
- `normalize_text_key`
- `normalize_url`
- `dedupe_records`

### Bad exception handling

OLD: Pipeline had no per-stage isolation; RSS/OpenAI/personnel/jobs failures could stop the run.

NEW: `app/services/intelligence_pipeline.py` uses `_safe_step` around each stage and continues with defaults.

### Performance bottlenecks

- Existing services query once per item. This is acceptable for current small crawler batch sizes but should be replaced by bulk prefetch/upsert when batch sizes grow.
- Context page probing still performs multiple HTTP requests; now each has short timeouts and retries.
- OpenAI calls remain sequential; this is safer for rate limits, but async batching can be added later.

## Phase 2 Data Quality Layer

Implemented in `app/services/data_quality.py`.

Jobs now require:

- title length between 6 and 120
- no URLs
- role-like title term
- no navigation terms
- no `Home`, `Products`, `Features`, `Resources`, `Download`, `Blog`, `AI`, `Pricing`, `Skip to content`

Personnel now require:

- person-like first/last-name shape
- no URLs
- no article/customer-story/marketing/product/news terms
- 2 to 5 name tokens

News now requires:

- valid title length
- non-navigation title
- uniqueness by title and URL per company in save layer

## Phase 3 Database Hardening

Generated:

- `database/001_cleanup_duplicates.sql`
- `database/002_add_unique_constraints.sql`

Run cleanup first, then constraints.

## Phase 4 Pipeline Hardening

`app/services/intelligence_pipeline.py`

OLD:

- One exception could abort the entire run.
- Existing company was updated, but child records still duplicated in several tables.

NEW:

- Every stage is wrapped in `_safe_step`.
- Existing company updates remain.
- Child writes are idempotent/upserted where required.
- Pipeline continues if RSS, OpenAI, personnel scraping, or job scraping fails.

## Phase 5 Crawler Improvements

Implemented for:

- `app/crawlers/context_graph_builder.py`
- `app/crawlers/job_scraper.py`
- `app/crawlers/personnel_scraper.py`
- `app/crawlers/blog_scraper.py`
- `app/crawlers/news_scraper.py`

Each now has some combination of:

- content filtering
- deduplication
- validation
- logging
- timeout/retry protection

## Phase 6 Cleanup Scripts

`database/001_cleanup_duplicates.sql` removes duplicates while keeping the oldest row for:

- competitors
- jobs
- personnel
- alerts
- news by title
- news by URL
- signal summaries
- briefings

## Phase 7 Code Changes

### New files

- OLD: No shared quality module.
- NEW: `app/services/data_quality.py`

- OLD: Crawlers used direct `requests.get` inconsistently.
- NEW: `app/utils/http_client.py`

- OLD: No `app/utils` package.
- NEW: `app/utils/__init__.py`

- OLD: No SQL hardening scripts.
- NEW: `database/001_cleanup_duplicates.sql`, `database/002_add_unique_constraints.sql`

### Modified files

- `app/services/competitor_service.py`
  - OLD: exact raw insert check.
  - NEW: normalized, per-batch dedupe, case-insensitive existing check.

- `app/services/job_listing_service.py`
  - OLD: exact title check and insert.
  - NEW: job validation, per-batch dedupe, case-insensitive existing check, URL update.

- `app/services/personnel_service.py`
  - OLD: embedded blocklist validation.
  - NEW: shared person validator, dedupe, case-insensitive lookup, role update.

- `app/services/news_article_service.py`
  - OLD: title-only duplicate check.
  - NEW: title and URL duplicate checks, validation, source-type preservation.

- `app/services/alert_service.py`
  - OLD: always insert.
  - NEW: return existing alert for same `(company_id, message)`.

- `app/services/briefing_service.py`
  - OLD: always insert.
  - NEW: update existing briefing for company.

- `app/services/signal_summary_service.py`
  - OLD: always insert.
  - NEW: update existing `(company_id, signal_type)` summary.

- `app/services/alert_engine.py`
  - OLD: raw title set comparison and alert duplication.
  - NEW: normalized title comparison and job validation before alert.

- `app/services/intelligence_pipeline.py`
  - OLD: linear hard-fail pipeline.
  - NEW: safe-stage pipeline with fallbacks.

- `app/crawlers/context_graph_builder.py`
  - OLD: broad link matching and direct requests.
  - NEW: same-site discovery, retrying HTTP, fallback probes, logging.

- `app/crawlers/job_scraper.py`
  - OLD: broad anchor text extraction.
  - NEW: job URL hints plus shared job validation.

- `app/crawlers/personnel_scraper.py`
  - OLD: unfiltered page text and raw AI output.
  - NEW: removes layout noise, validates and dedupes AI output.

- `app/crawlers/blog_scraper.py`
  - OLD: simple blog path filtering.
  - NEW: shared article validation and URL dedupe.

- `app/crawlers/news_scraper.py`
  - OLD: feedparser fetched URL directly.
  - NEW: timeout/retry fetch, parser warning handling, validation, dedupe.

- `app/crawlers/greenhouse_scraper.py`
  - OLD: local invalid title list.
  - NEW: shared job validation and dedupe.

- `app/ai/briefing_generator.py`
  - OLD: no API exception fallback.
  - NEW: timeout and fallback briefing.

- `app/ai/competitor_analyzer.py`
  - OLD: weaker prompt and no API exception fallback.
  - NEW: stricter prompt and fallback `[]`.

- `app/ai/leadership_analyzer.py`
  - OLD: weaker prompt and no API exception fallback.
  - NEW: stricter prompt and fallback `[]`.

- `app/ai/news_analyzer.py`
  - OLD: no API exception fallback.
  - NEW: timeout and fallback summary.

- `app/models/*.py`
  - OLD: no uniqueness constraints on affected tables.
  - NEW: uniqueness constraints matching requested keys.

## Verification

- `python -m compileall app` passed.
- Validator checks passed for:
  - valid job: `Senior Software Engineer`
  - invalid jobs: `AI Engineer`, `Pricing`, `Products`, `Skip to content`
  - valid job preserved: `Product Manager`
  - valid person: `Jane Doe`
  - invalid personnel: article title, URL, customer story
  - valid/invalid news title checks
- `python test_news_scraper.py` passed against live Google News RSS.
- `python test_jobs.py` passed against live Stripe careers page and returned job listings.
- `pytest` could not be run because `pytest` is not installed in this Python environment.
