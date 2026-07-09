import logging
import re
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from crawler.utils import (
    HEADERS,
    clean_text,
    clean_url,
    collect_enriched_jobs,
    fetch_soup,
    sleep,
)

BASE_URL = "https://jobinja.ir"
START_URL = "https://jobinja.ir/jobs"
logger = logging.getLogger(__name__)


def clean_lines(value: str) -> str:
    lines = [clean_text(line) for line in value.splitlines()]
    boilerplate = ("ثبت آگهی استخدام در جابینجا",)
    return "\n".join(
        line for line in lines if line and not any(text in line for text in boilerplate)
    )


def fetch_page(url: str, session: requests.Session) -> BeautifulSoup:
    return fetch_soup(url, session, headers=HEADERS)


def parse_jobs(soup: BeautifulSoup):
    jobs = []
    seen_urls = set()

    for card in soup.select("li.c-jobListView__item"):
        link = card.select_one("a.c-jobListView__titleLink")
        if not link:
            continue

        title = clean_text(link.get_text())
        href = link.get("href")

        if not title or not href:
            continue

        job_url = clean_url(urljoin(BASE_URL, href))

        if (
            "/companies/" not in job_url
            or "/jobs/" not in job_url
            or job_url in seen_urls
        ):
            continue

        seen_urls.add(job_url)

        company = ""
        location = ""
        contract = ""
        published = clean_text(
            card.select_one(".c-jobListView__passedDays").get_text()
            if card.select_one(".c-jobListView__passedDays")
            else ""
        )

        meta_items = card.select(".c-jobListView__metaItem")
        if len(meta_items) > 0:
            company = clean_text(meta_items[0].get_text(" "))
        if len(meta_items) > 1:
            location = clean_text(meta_items[1].get_text(" "))
        if len(meta_items) > 2:
            contract = clean_text(meta_items[2].get_text(" "))
            contract = re.sub(r"\s*\(برای\s+مشاهده\s+حقوق.*?\)\s*", "", contract)
            contract = clean_text(contract)

        jobs.append(
            {
                "title": title,
                "company": company,
                "location": location,
                "contract": contract,
                "published": published,
                "url": job_url,
            }
        )

    return jobs


def get_info_box_value(soup: BeautifulSoup, title: str) -> str:
    for heading in soup.select(".c-infoBox__itemTitle"):
        if clean_text(heading.get_text()) != title:
            continue

        item = heading.find_parent("li")
        if not item:
            continue

        lines = [
            clean_text(line)
            for line in item.get_text("\n").splitlines()
            if clean_text(line)
        ]
        return clean_lines("\n".join(line for line in lines if line != title))

    return ""


def get_o_box_text(soup: BeautifulSoup, title: str) -> str:
    for heading in soup.select("h4.o-box__title"):
        if clean_text(heading.get_text()) != title:
            continue

        content = heading.find_next_sibling("div", class_="o-box__text")
        return clean_lines(content.get_text("\n")) if content else ""

    return ""


def parse_job_details(soup: BeautifulSoup):
    description = get_o_box_text(soup, "شرح موقعیت شغلی")
    company_intro = get_o_box_text(soup, "معرفی شرکت")
    job_description = clean_lines(f"{description}\n{company_intro}")

    return {
        "salary": get_info_box_value(soup, "حقوق"),
        "experience": get_info_box_value(soup, "حداقل سابقه کار"),
        "job_description": job_description,
    }


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
