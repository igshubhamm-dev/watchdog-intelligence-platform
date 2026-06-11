BEGIN;

WITH ranked AS (
    SELECT
        id,
        ROW_NUMBER() OVER (
            PARTITION BY company_id, lower(trim(competitor_name))
            ORDER BY created_at ASC NULLS LAST, id ASC
        ) AS row_number
    FROM competitors
)
DELETE FROM competitors
USING ranked
WHERE competitors.id = ranked.id
  AND ranked.row_number > 1;

WITH ranked AS (
    SELECT
        id,
        ROW_NUMBER() OVER (
            PARTITION BY company_id, lower(trim(title))
            ORDER BY created_at ASC NULLS LAST, id ASC
        ) AS row_number
    FROM job_listings
)
DELETE FROM job_listings
USING ranked
WHERE job_listings.id = ranked.id
  AND ranked.row_number > 1;

WITH ranked AS (
    SELECT
        id,
        ROW_NUMBER() OVER (
            PARTITION BY company_id, lower(trim(name))
            ORDER BY created_at ASC NULLS LAST, id ASC
        ) AS row_number
    FROM personnel
)
DELETE FROM personnel
USING ranked
WHERE personnel.id = ranked.id
  AND ranked.row_number > 1;

WITH ranked AS (
    SELECT
        id,
        ROW_NUMBER() OVER (
            PARTITION BY company_id, lower(trim(message))
            ORDER BY created_at ASC NULLS LAST, id ASC
        ) AS row_number
    FROM alerts
)
DELETE FROM alerts
USING ranked
WHERE alerts.id = ranked.id
  AND ranked.row_number > 1;

WITH ranked AS (
    SELECT
        id,
        ROW_NUMBER() OVER (
            PARTITION BY company_id, lower(trim(title))
            ORDER BY created_at ASC NULLS LAST, id ASC
        ) AS row_number
    FROM news_articles
)
DELETE FROM news_articles
USING ranked
WHERE news_articles.id = ranked.id
  AND ranked.row_number > 1;

WITH ranked AS (
    SELECT
        id,
        ROW_NUMBER() OVER (
            PARTITION BY company_id, lower(trim(url))
            ORDER BY created_at ASC NULLS LAST, id ASC
        ) AS row_number
    FROM news_articles
)
DELETE FROM news_articles
USING ranked
WHERE news_articles.id = ranked.id
  AND ranked.row_number > 1;

WITH ranked AS (
    SELECT
        id,
        ROW_NUMBER() OVER (
            PARTITION BY company_id, lower(trim(signal_type))
            ORDER BY created_at ASC NULLS LAST, id ASC
        ) AS row_number
    FROM signal_summaries
)
DELETE FROM signal_summaries
USING ranked
WHERE signal_summaries.id = ranked.id
  AND ranked.row_number > 1;

WITH ranked AS (
    SELECT
        id,
        ROW_NUMBER() OVER (
            PARTITION BY company_id
            ORDER BY created_at ASC NULLS LAST, id ASC
        ) AS row_number
    FROM briefings
)
DELETE FROM briefings
USING ranked
WHERE briefings.id = ranked.id
  AND ranked.row_number > 1;

COMMIT;
