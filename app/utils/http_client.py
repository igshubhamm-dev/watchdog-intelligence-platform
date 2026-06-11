import logging
from time import sleep

import requests


LOGGER = logging.getLogger(__name__)

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0 Safari/537.36"
    )
}


def get_url(url, timeout=15, retries=2, headers=None, params=None):
    merged_headers = dict(DEFAULT_HEADERS)
    if headers:
        merged_headers.update(headers)

    last_error = None

    for attempt in range(retries + 1):
        try:
            response = requests.get(
                url,
                timeout=timeout,
                headers=merged_headers,
                params=params,
            )
            response.raise_for_status()
            return response
        except requests.RequestException as exc:
            last_error = exc
            LOGGER.warning(
                "HTTP GET failed for %s on attempt %s/%s: %s",
                url,
                attempt + 1,
                retries + 1,
                exc,
            )
            if attempt < retries:
                sleep(0.5 * (attempt + 1))

    raise last_error
