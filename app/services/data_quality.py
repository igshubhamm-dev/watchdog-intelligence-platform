import re
from urllib.parse import urlparse


NAVIGATION_TERMS = {
    "home",
    "products",
    "features",
    "resources",
    "download",
    "downloads",
    "blog",
    "pricing",
    "skip to content",
    "skip to main content",
}

JOB_BLOCKLIST = NAVIGATION_TERMS | {
    "ai",
    "about",
    "about us",
    "careers",
    "contact",
    "customer stories",
    "customers",
    "login",
    "log in",
    "privacy",
    "request demo",
    "sign in",
    "solutions",
    "terms",
}

JOB_ROLE_TERMS = {
    "accountant",
    "analyst",
    "architect",
    "associate",
    "consultant",
    "coordinator",
    "designer",
    "developer",
    "director",
    "engineer",
    "executive",
    "lead",
    "manager",
    "marketer",
    "operator",
    "principal",
    "producer",
    "recruiter",
    "researcher",
    "scientist",
    "specialist",
    "strategist",
    "writer",
}

PERSON_BLOCKLIST = NAVIGATION_TERMS | {
    "article",
    "award",
    "blog",
    "case study",
    "client",
    "customer",
    "customer story",
    "customers",
    "guide",
    "headline",
    "insight",
    "learn",
    "marketing",
    "news",
    "newsletter",
    "platform",
    "press",
    "product",
    "report",
    "story",
    "webinar",
}

PERSON_PREFIX_BLOCKLIST = {
    "a ",
    "an ",
    "best ",
    "how ",
    "meet the ",
    "our ",
    "the ",
    "why ",
}


def compact_whitespace(value):
    return re.sub(r"\s+", " ", (value or "").strip())


def normalize_text_key(value):
    return compact_whitespace(value).casefold()


def normalize_url(value):
    if not value:
        return None

    parsed = urlparse(value.strip())
    if not parsed.scheme or not parsed.netloc:
        return value.strip()

    path = parsed.path.rstrip("/") or "/"
    return parsed._replace(
        scheme=parsed.scheme.lower(),
        netloc=parsed.netloc.lower(),
        path=path,
        fragment="",
    ).geturl()


def contains_url(value):
    return bool(re.search(r"https?://|www\.", value or "", re.IGNORECASE))


def has_blocked_phrase(value, blocked_terms):
    normalized = normalize_text_key(value)
    for term in blocked_terms:
        if len(term) <= 2:
            if re.search(rf"\b{re.escape(term)}\b", normalized):
                return True
            continue

        if term in normalized:
            return True

    return False


def is_valid_job_title(title):
    clean_title = compact_whitespace(title)
    normalized = clean_title.casefold()

    if len(clean_title) < 6 or len(clean_title) > 120:
        return False

    if contains_url(clean_title):
        return False

    if has_blocked_phrase(clean_title, JOB_BLOCKLIST):
        return False

    if not any(term in normalized for term in JOB_ROLE_TERMS):
        return False

    if re.search(r"[{}<>]|^\W+$", clean_title):
        return False

    return True


def is_valid_person_name(name):
    clean_name = compact_whitespace(name)
    normalized = clean_name.casefold()

    if len(clean_name) < 5 or len(clean_name) > 80:
        return False

    if contains_url(clean_name):
        return False

    if has_blocked_phrase(clean_name, PERSON_BLOCKLIST):
        return False

    if any(normalized.startswith(prefix) for prefix in PERSON_PREFIX_BLOCKLIST):
        return False

    if clean_name.endswith((".", "?", "!", ":")):
        return False

    if clean_name.isupper():
        return False

    words = clean_name.split()
    if len(words) < 2 or len(words) > 5:
        return False

    name_token = r"[A-Z][A-Za-z'-]+"
    if not re.fullmatch(rf"{name_token}(?:\s+{name_token}){{1,4}}", clean_name):
        return False

    return True


def is_valid_news_article(title, url=None):
    clean_title = compact_whitespace(title)

    if len(clean_title) < 8 or len(clean_title) > 250:
        return False

    if url and contains_url(clean_title):
        return False

    if normalize_text_key(clean_title) in NAVIGATION_TERMS:
        return False

    return True


def dedupe_records(records, key_func):
    deduped = []
    seen = set()

    for record in records or []:
        key = key_func(record)
        if not key or key in seen:
            continue

        seen.add(key)
        deduped.append(record)

    return deduped
