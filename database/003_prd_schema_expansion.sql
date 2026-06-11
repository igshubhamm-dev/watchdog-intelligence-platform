BEGIN;

ALTER TABLE personnel
    ADD COLUMN IF NOT EXISTS title TEXT,
    ADD COLUMN IF NOT EXISTS linkedin_url TEXT,
    ADD COLUMN IF NOT EXISTS first_seen TIMESTAMPTZ DEFAULT now(),
    ADD COLUMN IF NOT EXISTS last_seen TIMESTAMPTZ DEFAULT now(),
    ADD COLUMN IF NOT EXISTS status TEXT NOT NULL DEFAULT 'active';

UPDATE personnel
SET title = COALESCE(title, role)
WHERE title IS NULL;

ALTER TABLE job_listings
    ADD COLUMN IF NOT EXISTS url TEXT,
    ADD COLUMN IF NOT EXISTS first_seen TIMESTAMPTZ DEFAULT now(),
    ADD COLUMN IF NOT EXISTS last_seen TIMESTAMPTZ DEFAULT now(),
    ADD COLUMN IF NOT EXISTS status TEXT NOT NULL DEFAULT 'active';

UPDATE job_listings
SET url = COALESCE(url, job_url)
WHERE url IS NULL;

ALTER TABLE signal_summaries
    ADD COLUMN IF NOT EXISTS category TEXT,
    ADD COLUMN IF NOT EXISTS summary_json JSONB,
    ADD COLUMN IF NOT EXISTS narrative TEXT,
    ADD COLUMN IF NOT EXISTS key_changes JSONB,
    ADD COLUMN IF NOT EXISTS so_what TEXT;

UPDATE signal_summaries
SET category = COALESCE(category, signal_type),
    narrative = COALESCE(narrative, summary),
    key_changes = COALESCE(key_changes, '[]'::jsonb)
WHERE category IS NULL
   OR narrative IS NULL
   OR key_changes IS NULL;

ALTER TABLE briefings
    ADD COLUMN IF NOT EXISTS briefing_md TEXT,
    ADD COLUMN IF NOT EXISTS briefing_json JSONB;

UPDATE briefings
SET briefing_md = COALESCE(briefing_md, brief)
WHERE briefing_md IS NULL;

CREATE TABLE IF NOT EXISTS ad_creatives (
    id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL REFERENCES companies(id),
    platform TEXT NOT NULL,
    ad_text TEXT NOT NULL,
    image_url_desc TEXT,
    started_at TEXT,
    ended_at TEXT,
    spend_range TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS social_posts (
    id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL REFERENCES companies(id),
    platform TEXT NOT NULL,
    post_text TEXT,
    url TEXT NOT NULL,
    posted_at TEXT,
    engagement TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS reviews (
    id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL REFERENCES companies(id),
    source TEXT NOT NULL,
    rating TEXT,
    review_text TEXT,
    review_date TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS brand_mentions (
    id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL REFERENCES companies(id),
    source TEXT NOT NULL,
    title TEXT NOT NULL,
    url TEXT NOT NULL,
    author TEXT,
    score TEXT,
    published_at TEXT,
    sentiment TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS wikipedia_snapshots (
    id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL REFERENCES companies(id),
    page_id TEXT NOT NULL,
    page_title TEXT NOT NULL,
    revision_id TEXT NOT NULL,
    url TEXT,
    summary TEXT,
    raw_data JSONB,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS tech_stack_snapshots (
    id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL REFERENCES companies(id),
    source_url TEXT NOT NULL,
    technologies JSONB NOT NULL,
    raw_data JSONB,
    created_at TIMESTAMPTZ DEFAULT now()
);

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'uq_ad_creatives_company_platform_text'
    ) THEN
        ALTER TABLE ad_creatives
        ADD CONSTRAINT uq_ad_creatives_company_platform_text
        UNIQUE (company_id, platform, ad_text);
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'uq_social_posts_company_platform_url'
    ) THEN
        ALTER TABLE social_posts
        ADD CONSTRAINT uq_social_posts_company_platform_url
        UNIQUE (company_id, platform, url);
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'uq_reviews_company_source_text_date'
    ) THEN
        ALTER TABLE reviews
        ADD CONSTRAINT uq_reviews_company_source_text_date
        UNIQUE (company_id, source, review_text, review_date);
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'uq_brand_mentions_company_source_url'
    ) THEN
        ALTER TABLE brand_mentions
        ADD CONSTRAINT uq_brand_mentions_company_source_url
        UNIQUE (company_id, source, url);
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'uq_wikipedia_snapshots_company_page_revision'
    ) THEN
        ALTER TABLE wikipedia_snapshots
        ADD CONSTRAINT uq_wikipedia_snapshots_company_page_revision
        UNIQUE (company_id, page_id, revision_id);
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'uq_tech_stack_snapshots_company_source'
    ) THEN
        ALTER TABLE tech_stack_snapshots
        ADD CONSTRAINT uq_tech_stack_snapshots_company_source
        UNIQUE (company_id, source_url);
    END IF;
END $$;

COMMIT;
