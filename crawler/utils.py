import logging
import time
from urllib.parse import urlsplit, urlunsplit

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)
REQUEST_TIMEOUT = 20

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) "
        "AppleWebKit/537.36 Chrome/120.0 Safari/537.36"
    )
}


def clean_text(value: str | None) -> str:
    return " ".join(value.split()) if value else ""


def clean_lines(value: str | None) -> str:
    lines = [clean_text(line) for line in (value or "").splitlines()]
    return "\n".join(line for line in lines if line)


def clean_url(url: str) -> str:
    parts = urlsplit(url)
    return urlunsplit((parts.scheme, parts.netloc, parts.path, "", ""))


def fetch_soup(
    url: str,
    session: requests.Session,
    *,
    headers: dict | None = None,
    strip_scripts: bool = False,
) -> BeautifulSoup:
    response = session.get(url, headers=headers or HEADERS, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "lxml")
    if strip_scripts:
        for tag in soup(["script", "style"]):
            tag.decompose()
    return soup


def html_to_text(value: str | None) -> str:
    soup = BeautifulSoup(value or "", "lxml")
    for tag in soup(["script", "style"]):
        tag.decompose()
    return clean_lines(soup.get_text("\n"))


def unique(values) -> list[str]:
    items = []
    for value in values:
        text = clean_text(value)
        if text and text not in items:
            items.append(text)
    return items


def sleep(delay_seconds: float) -> None:
    if delay_seconds > 0:
        time.sleep(delay_seconds)


def collect_enriched_jobs(
    *,
    jobs: list[dict],
    all_jobs: list[dict],
    seen_urls: set[str],
    session: requests.Session,
    enrich_job,
    delay_seconds: float,
    source_logger=None,
) -> None:
    source_logger = source_logger or logger

    for job in jobs:
        url = job.get("url")
        title = job.get("title", "")
        if not url or url in seen_urls:
            continue

        seen_urls.add(url)
        source_logger.info("Fetching detail: %s", title or url)

        try:
            all_jobs.append(enrich_job(job, session))
        except Exception as exc:
            source_logger.warning("Skipping detail page %s: %s", url, exc)

        sleep(delay_seconds)
