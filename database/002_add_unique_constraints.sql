BEGIN;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'uq_competitors_company_name'
    ) THEN
        ALTER TABLE competitors
        ADD CONSTRAINT uq_competitors_company_name
        UNIQUE (company_id, competitor_name);
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'uq_personnel_company_name'
    ) THEN
        ALTER TABLE personnel
        ADD CONSTRAINT uq_personnel_company_name
        UNIQUE (company_id, name);
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'uq_job_listings_company_title'
    ) THEN
        ALTER TABLE job_listings
        ADD CONSTRAINT uq_job_listings_company_title
        UNIQUE (company_id, title);
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'uq_news_articles_company_title'
    ) THEN
        ALTER TABLE news_articles
        ADD CONSTRAINT uq_news_articles_company_title
        UNIQUE (company_id, title);
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'uq_news_articles_company_url'
    ) THEN
        ALTER TABLE news_articles
        ADD CONSTRAINT uq_news_articles_company_url
        UNIQUE (company_id, url);
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'uq_alerts_company_message'
    ) THEN
        ALTER TABLE alerts
        ADD CONSTRAINT uq_alerts_company_message
        UNIQUE (company_id, message);
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'uq_signal_summaries_company_type'
    ) THEN
        ALTER TABLE signal_summaries
        ADD CONSTRAINT uq_signal_summaries_company_type
        UNIQUE (company_id, signal_type);
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'uq_briefings_company'
    ) THEN
        ALTER TABLE briefings
        ADD CONSTRAINT uq_briefings_company
        UNIQUE (company_id);
    END IF;
END $$;

COMMIT;
