import logging

import requests
from bs4 import BeautifulSoup

from crawler.utils import (
    HEADERS,
    clean_lines,
    clean_text,
    clean_url,
    collect_enriched_jobs,
    fetch_soup,
    sleep,
)

START_URL = "https://karboom.io/jobs"
logger = logging.getLogger(__name__)


def fetch_page(url: str, session: requests.Session) -> BeautifulSoup:
    return fetch_soup(url, session, headers=HEADERS)


def parse_jobs(soup: BeautifulSoup):
    jobs = []
    seen_urls = set()

    for card in soup.select("div.box-intro.js-job-item.flex-col-between"):
        title = get_card_text(card, "h3.sm-title-size")
        link = card.find("a", class_="no-text-decoration", href=True)
        if not title or not link:
            continue

        job_url = clean_url(link["href"])
        if job_url in seen_urls:
            continue

        seen_urls.add(job_url)
        jobs.append(
            {
                "title": title,
                "company": get_card_text(card, "span.company-name"),
                "location": get_card_text(card, "span.pull-right"),
                "published": get_published(card),
                "salary": "",
                "url": job_url,
                "job_description": "",
            }
        )

    return jobs


def get_card_text(card, selector: str) -> str:
    item = card.select_one(selector)
    return clean_text(item.get_text(" ")) if item else ""


def get_published(card) -> str:
    item = card.select_one("p.immediate-employment, p.date")
    return clean_text(item.get_text(" ")) if item else ""


def parse_job_details(soup: BeautifulSoup):
    return {
        "salary": get_salary(soup),
        "job_description": get_job_description(soup),
    }


def get_salary(soup: BeautifulSoup) -> str:
    salary = soup.select_one(".job-info .kb-text-gray-medium")
    return clean_text(salary.get_text(" ")) if salary else ""


def get_job_description(soup: BeautifulSoup) -> str:
    for box in soup.select("div.job-detail-box"):
        heading = box.find(["h2", "h3", "h4"])
        if not heading or "شرح شغل" not in clean_text(heading.get_text(" ")):
            continue

        description = box.find("div", class_="md-text-size")
        return clean_lines(description.get_text("\n")) if description else ""

    return ""


def enrich_job_details(job, session: requests.Session):
    soup = fetch_page(job["url"], session)
    return {**job, **parse_job_details(soup)}


def crawl(max_pages: int = 2, delay_seconds: float = 2.0):
    all_jobs = []
    seen_urls = set()
    session = requests.Session()

    for page in range(1, max_pages + 1):
        url = f"{START_URL}?page={page}"
        logger.info("Crawling: %s", url)

        try:
            soup = fetch_page(url, session)
            jobs = parse_jobs(soup)
        except Exception as exc:
            logger.warning("Skipping page %s: %s", url, exc)
            sleep(delay_seconds)
            continue

        collect_enriched_jobs(
            jobs=jobs,
            all_jobs=all_jobs,
            seen_urls=seen_urls,
            session=session,
            enrich_job=enrich_job_details,
            delay_seconds=delay_seconds,
            source_logger=logger,
        )
        sleep(delay_seconds)

    return all_jobs
