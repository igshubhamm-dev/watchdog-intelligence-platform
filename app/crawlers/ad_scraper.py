import logging
import os

from app.utils.http_client import get_url


LOGGER = logging.getLogger(__name__)


def scrape_meta_ads(company_name):
    access_token = os.getenv("META_AD_LIBRARY_ACCESS_TOKEN")
    if not company_name or not access_token:
        return []

    try:
        response = get_url(
            "https://graph.facebook.com/v19.0/ads_archive",
            timeout=20,
            retries=2,
            params={
                "search_terms": company_name,
                "ad_reached_countries": "['US']",
                "fields": (
                    "ad_creative_bodies,ad_creative_link_descriptions,"
                    "ad_delivery_start_time,ad_delivery_stop_time,spend"
                ),
                "access_token": access_token,
            },
        )
        payload = response.json()
    except Exception as exc:
        LOGGER.exception("Meta Ad Library scrape failed for %s", company_name)
        print("META ADS ERROR:", exc)
        return []

    ads = []
    for item in payload.get("data", [])[:50]:
        bodies = item.get("ad_creative_bodies") or []
        ad_text = " ".join(bodies).strip()
        if not ad_text:
            continue

        spend = item.get("spend") or {}
        ads.append({
            "platform": "meta",
            "ad_text": ad_text,
            "image_url_desc": " ".join(item.get("ad_creative_link_descriptions") or []),
            "started_at": item.get("ad_delivery_start_time"),
            "ended_at": item.get("ad_delivery_stop_time"),
            "spend_range": (
                f"{spend.get('lower_bound')} - {spend.get('upper_bound')}"
                if spend
                else None
            ),
        })

    return ads


def scrape_google_ads(company_name):
    return []


def scrape_linkedin_ads(company_name):
    return []


def scrape_ads(company_name):
    ads = []
    ads.extend(scrape_meta_ads(company_name))
    ads.extend(scrape_google_ads(company_name))
    ads.extend(scrape_linkedin_ads(company_name))
    return ads
