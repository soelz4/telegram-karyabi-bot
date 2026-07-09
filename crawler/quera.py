import logging
import re
from urllib.parse import urljoin

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

BASE_URL = "https://quera.org"
START_URL = "https://quera.org/magnet/jobs"
logger = logging.getLogger(__name__)

EXPERIENCE_LEVELS = {
    "Intern",
    "Junior",
    "Mid-level",
    "Senior",
    "Lead",
    "Manager",
}


def fetch_page(url: str, session: requests.Session) -> BeautifulSoup:
    return fetch_soup(url, session, headers=HEADERS, strip_scripts=True)


def parse_jobs(soup: BeautifulSoup):
    jobs = []
    seen_urls = set()

    for article in soup.find_all("article"):
        link = article.find("a", href=re.compile(r"^/magnet/jobs/[a-z0-9]+$"))
        title_tag = article.find("h2")
        if not link or not title_tag:
            continue

        job_url = clean_url(urljoin(BASE_URL, link["href"]))
        if job_url in seen_urls:
            continue

        title = clean_text(title_tag.get_text(" "))
        if not title:
            continue

        seen_urls.add(job_url)
        jobs.append(
            {
                "title": title,
                "company": get_company(article),
                "location": get_location(article),
                "experience": get_experience(article),
                "published": get_published(article),
                "published_at": get_published_at(article),
                "url": job_url,
                "job_description": "",
                "tags": "",
                "company_description": "",
            }
        )

    return jobs


def get_company(article) -> str:
    company = article.select_one("p.chakra-text")
    return clean_text(company.get_text(" ")) if company else ""


def get_location(article) -> str:
    company = article.select_one("p.chakra-text")
    if not company:
        return ""

    company_stack = company.find_parent("div", class_=has_chakra_stack)
    if not company_stack:
        return ""

    location_stack = company_stack.find_next_sibling("div", class_=has_chakra_stack)
    return clean_text(location_stack.get_text(" ")) if location_stack else ""


def get_experience(article) -> str:
    for span in article.find_all("span"):
        text = clean_text(span.get_text(" "))
        if text in EXPERIENCE_LEVELS:
            return text
    return ""


def get_published(article) -> str:
    published = article.find("span", title=True)
    return clean_text(published.get_text(" ")) if published else ""


def get_published_at(article) -> str:
    published = article.find("span", title=True)
    return clean_text(published["title"]) if published else ""


def has_chakra_stack(classes) -> bool:
    return bool(classes and "chakra-stack" in classes)


def enrich_job_details(job, session: requests.Session):
    soup = fetch_page(job["url"], session)
    return {**job, **parse_job_details(soup)}


def parse_job_details(soup: BeautifulSoup):
    company_info = get_company_info(soup)
    return {
        "job_description": get_section_text(soup, "توضیحات فرصت شغلی"),
        "tags": "\n".join(get_tags(soup)),
        **company_info,
    }


def get_section_text(soup: BeautifulSoup, title: str) -> str:
    heading = find_heading(soup, title)
    if not heading:
        return ""

    content = heading.find_next_sibling("div")
    if not content:
        return ""

    return clean_lines(content.get_text("\n"))


def get_tags(soup: BeautifulSoup) -> list[str]:
    heading = find_heading(soup, "تکنولوژی‌ها")
    if not heading:
        return []

    section = heading.find_next_sibling("div")
    if not section:
        return []

    tags = []
    for item in section.find_all("span"):
        text = clean_text(item.get_text(" "))
        if text and text not in tags:
            tags.append(text)
    return tags


def get_company_info(soup: BeautifulSoup):
    company_section = get_company_section(soup)
    if not company_section:
        return {"company_description": ""}

    meta_items = [
        clean_text(item.get_text(" "))
        for item in company_section.select("p.chakra-text")
        if clean_text(item.get_text(" "))
    ]
    description_parts = [*meta_items, *get_company_description_sections(company_section)]
    return {"company_description": "\n".join(part for part in description_parts if part)}


def get_company_section(soup: BeautifulSoup):
    for section in soup.find_all("div", class_=has_chakra_stack):
        if not section.select_one("p.chakra-text"):
            continue
        if not section.find(
            "div", class_=lambda value: value and "css-1aq9j02" in value
        ):
            continue

        headings = {
            clean_text(heading.get_text(" ")) for heading in section.find_all("h2")
        }
        if headings.isdisjoint({"توضیحات فرصت شغلی", "تکنولوژی‌ها"}):
            return section

    return None


def get_company_description_sections(company_section) -> list[str]:
    sections = []

    for content in company_section.find_all(
        "div", class_=lambda value: value and "css-1aq9j02" in value
    ):
        content_text = clean_lines(content.get_text("\n"))
        if not content_text:
            continue

        heading = content.find_previous("h2")
        heading_text = ""
        if heading and company_section in heading.parents:
            if not heading.select_one("a[href^='/magnet/companies/']"):
                heading_text = clean_text(heading.get_text(" "))

        section_text = f"{heading_text}\n{content_text}" if heading_text else content_text
        if section_text not in sections:
            sections.append(section_text)

    return sections


def find_heading(soup: BeautifulSoup, title: str):
    for heading in soup.find_all("h2"):
        if clean_text(heading.get_text(" ")) == title:
            return heading
    return None


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
