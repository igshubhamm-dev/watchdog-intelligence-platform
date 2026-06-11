import logging
from urllib.parse import urlparse

from app.ai.briefing_generator import generate_brief
from app.ai.competitor_analyzer import discover_competitors
from app.ai.signal_distiller import distill_signal
from app.crawlers.ad_scraper import scrape_ads
from app.crawlers.blog_scraper import scrape_blog_posts
from app.crawlers.context_graph_builder import build_context_graph
from app.crawlers.job_scraper import scrape_jobs
from app.crawlers.news_scraper import search_company_news
from app.crawlers.personnel_scraper import scrape_personnel
from app.crawlers.quora_scraper import scrape_quora_mentions
from app.crawlers.reddit_scraper import scrape_reddit_mentions
from app.crawlers.review_scraper import scrape_reviews
from app.crawlers.social_scraper import scrape_social_posts
from app.crawlers.tech_stack_scraper import detect_tech_stack
from app.crawlers.wikipedia_scraper import scrape_wikipedia_snapshot
from app.db.database import SessionLocal
from app.models.signal_summary import SignalSummary
from app.services.ad_creative_service import save_ad_creatives
from app.services.alert_engine import detect_new_jobs
from app.services.brand_mention_service import save_brand_mentions
from app.services.briefing_service import save_briefing
from app.services.company_service import save_company
from app.services.competitor_service import save_competitors
from app.services.job_listing_service import save_job_listings
from app.services.news_article_service import save_news_articles
from app.services.personnel_service import save_personnel
from app.services.review_service import save_reviews
from app.services.scrape_run_service import save_scrape_run
from app.services.signal_summary_service import save_signal_summary
from app.services.social_post_service import save_social_posts
from app.services.tech_stack_snapshot_service import save_tech_stack_snapshot
from app.services.wikipedia_snapshot_service import save_wikipedia_snapshots


LOGGER = logging.getLogger(__name__)


def _safe_step(step_name, func, default):
    try:
        return func()
    except Exception as exc:
        LOGGER.exception("%s failed", step_name)
        print(f"{step_name.upper()} ERROR:", exc)
        return default


def _company_query_from_url(url):
    domain_name = (
        urlparse(url)
        .netloc
        .replace("www.", "")
        .split(".")[0]
    )
    return domain_name.title()


def _previous_summary(company_id, category):
    db = SessionLocal()
    try:
        record = (
            db.query(SignalSummary)
            .filter(
                SignalSummary.company_id == company_id,
                SignalSummary.signal_type == category,
            )
            .first()
        )
        if not record:
            return None
        return record.summary_json or {
            "narrative": record.narrative or record.summary,
            "key_changes": record.key_changes or [],
            "so_what": record.so_what,
        }
    finally:
        db.close()


def _record_scrape(company_id, category, status, raw_data):
    return _safe_step(
        f"{category} scrape run save",
        lambda: save_scrape_run(
            company_id=company_id,
            category=category,
            status=status,
            raw_data=raw_data,
        ),
        None,
    )


def _distill_and_save(company_id, category, raw_data):
    previous = _safe_step(
        f"{category} previous summary lookup",
        lambda: _previous_summary(company_id, category),
        None,
    )
    summary = _safe_step(
        f"{category} distillation",
        lambda: distill_signal(category, raw_data, previous),
        {
            "category": category,
            "signals_changed": False,
            "key_changes": [],
            "narrative": "No public signal data was available for this category.",
            "so_what": "No competitive implication can be determined from available public data.",
        },
    )
    _safe_step(
        f"{category} summary save",
        lambda: save_signal_summary(
            company_id=company_id,
            signal_type=category,
            summary=summary,
            narrative=summary.get("narrative"),
            key_changes=summary.get("key_changes"),
            so_what=summary.get("so_what"),
        ),
        None,
    )
    return summary


def _run_category(company_id, category, scrape_func, save_func):
    raw_data = _safe_step(f"{category} scrape", scrape_func, [])
    status = "success" if raw_data else "partial"
    _record_scrape(company_id, category, status, raw_data)
    _safe_step(f"{category} raw save", lambda: save_func(raw_data), 0)
    return _distill_and_save(company_id, category, raw_data)


def analyze_company_pipeline(url):
    context_graph = _safe_step(
        "context graph",
        lambda: build_context_graph(url),
        {
            "website": url,
            "title": None,
            "description": "Unable to crawl company website.",
            "social_links": [],
            "about_page": None,
            "careers_page": None,
            "careers_pages": [],
            "blog_page": None,
            "rss_feed_url": None,
            "news_page": None,
            "press_page": None,
        },
    )

    if (
        context_graph.get("title") is None
        and context_graph.get("description")
        == "Unable to crawl company website."
    ):
        return {
            "company_id": None,
            "company_name": None,
            "context_graph": context_graph,
            "summary": "Unable to crawl company website.",
            "brief": "Analysis aborted.",
        }

    company = _safe_step(
        "company save",
        lambda: save_company(url=url, context_graph=context_graph),
        None,
    )

    if not company:
        return {
            "company_id": None,
            "company_name": None,
            "context_graph": context_graph,
            "summary": "Unable to save company.",
            "brief": "Analysis aborted.",
        }

    company_query = company.name or _company_query_from_url(url)
    category_summaries = {}

    blog_source = context_graph.get("rss_feed_url") or context_graph.get("blog_page")
    category_summaries["blog"] = _run_category(
        company.id,
        "blog",
        lambda: scrape_blog_posts(blog_source),
        lambda raw: save_news_articles(company.id, raw, source_type="BLOG"),
    )

    competitors = _safe_step(
        "competitor discovery",
        lambda: discover_competitors(
            company_name=company_query,
            description=context_graph.get("description") or "",
        ),
        [],
    )
    _record_scrape(company.id, "competitors", "success" if competitors else "partial", competitors)
    _safe_step(
        "competitor save",
        lambda: save_competitors(company.id, competitors),
        0,
    )
    category_summaries["competitors"] = _distill_and_save(
        company.id,
        "competitors",
        competitors,
    )

    jobs = _safe_step(
        "jobs scrape",
        lambda: scrape_jobs(context_graph.get("careers_page")),
        [],
    )
    _record_scrape(company.id, "jobs", "success" if jobs else "partial", jobs)
    _safe_step(
        "job alert detection",
        lambda: detect_new_jobs(company.id, jobs),
        None,
    )
    _safe_step(
        "job save",
        lambda: save_job_listings(company.id, jobs),
        0,
    )
    category_summaries["jobs"] = _distill_and_save(company.id, "jobs", jobs)

    personnel = _safe_step(
        "personnel scrape",
        lambda: scrape_personnel(context_graph.get("about_page")),
        [],
    )
    _record_scrape(
        company.id,
        "personnel",
        "success" if personnel else "partial",
        personnel,
    )
    _safe_step(
        "personnel save",
        lambda: save_personnel(company.id, personnel),
        0,
    )
    context_graph["leadership_team"] = personnel
    category_summaries["personnel"] = _distill_and_save(
        company.id,
        "personnel",
        personnel,
    )

    news = _safe_step(
        "news search",
        lambda: search_company_news(company_query),
        [],
    )
    _record_scrape(company.id, "news", "success" if news else "partial", news)
    _safe_step(
        "news save",
        lambda: save_news_articles(company.id, news),
        0,
    )
    category_summaries["news"] = _distill_and_save(company.id, "news", news)

    category_summaries["social"] = _run_category(
        company.id,
        "social",
        lambda: scrape_social_posts(context_graph.get("social_links")),
        lambda raw: save_social_posts(company.id, raw),
    )

    category_summaries["ads"] = _run_category(
        company.id,
        "ads",
        lambda: scrape_ads(company_query),
        lambda raw: save_ad_creatives(company.id, raw),
    )

    category_summaries["reviews"] = _run_category(
        company.id,
        "reviews",
        lambda: scrape_reviews(company_query),
        lambda raw: save_reviews(company.id, raw),
    )

    reddit_mentions = _safe_step(
        "reddit scrape",
        lambda: scrape_reddit_mentions(company_query),
        [],
    )
    quora_mentions = _safe_step(
        "quora scrape",
        lambda: scrape_quora_mentions(company_query),
        [],
    )
    brand_mentions = reddit_mentions + quora_mentions
    _record_scrape(
        company.id,
        "brand_mentions",
        "success" if brand_mentions else "partial",
        brand_mentions,
    )
    _safe_step(
        "brand mentions save",
        lambda: save_brand_mentions(company.id, brand_mentions),
        0,
    )
    category_summaries["brand_mentions"] = _distill_and_save(
        company.id,
        "brand_mentions",
        brand_mentions,
    )

    wikipedia_snapshots = _safe_step(
        "wikipedia scrape",
        lambda: scrape_wikipedia_snapshot(company_query),
        [],
    )
    _record_scrape(
        company.id,
        "wikipedia",
        "success" if wikipedia_snapshots else "partial",
        wikipedia_snapshots,
    )
    _safe_step(
        "wikipedia save",
        lambda: save_wikipedia_snapshots(company.id, wikipedia_snapshots),
        0,
    )
    category_summaries["wikipedia"] = _distill_and_save(
        company.id,
        "wikipedia",
        wikipedia_snapshots,
    )

    tech_stack = _safe_step(
        "tech stack scrape",
        lambda: detect_tech_stack(url),
        None,
    )
    tech_stack_raw = [tech_stack] if tech_stack else []
    _record_scrape(
        company.id,
        "technology_stack",
        "success" if tech_stack else "partial",
        tech_stack_raw,
    )
    _safe_step(
        "tech stack save",
        lambda: save_tech_stack_snapshot(company.id, tech_stack),
        None,
    )
    context_graph["tech_stack_snapshot"] = tech_stack
    category_summaries["technology_stack"] = _distill_and_save(
        company.id,
        "technology_stack",
        tech_stack_raw,
    )

    _safe_step(
        "company context graph enrichment save",
        lambda: save_company(url=url, context_graph=context_graph),
        None,
    )

    brief = _safe_step(
        "briefing generation",
        lambda: generate_brief(category_summaries, company.name),
        "Executive briefing unavailable.",
    )
    _safe_step(
        "briefing save",
        lambda: save_briefing(
            company.id,
            brief,
            briefing_json={
                "company_id": company.id,
                "company_name": company.name,
                "category_summaries": category_summaries,
            },
        ),
        None,
    )

    return {
        "company_id": company.id,
        "company_name": company.name,
        "context_graph": context_graph,
        "summary": category_summaries.get("news", {}).get("narrative", ""),
        "summaries": category_summaries,
        "brief": brief,
    }
