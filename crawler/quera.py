import re
import time
from urllib.parse import urljoin, urlsplit, urlunsplit

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://quera.org"
START_URL = "https://quera.org/magnet/jobs"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) "
        "AppleWebKit/537.36 Chrome/120.0 Safari/537.36"
    )
}

EXPERIENCE_LEVELS = {
    "Intern",
    "Junior",
    "Mid-level",
    "Senior",
    "Lead",
    "Manager",
}


def clean_text(value: str) -> str:
    return " ".join(value.split()) if value else ""


def clean_url(url: str) -> str:
    parts = urlsplit(url)
    return urlunsplit((parts.scheme, parts.netloc, parts.path, "", ""))


def fetch_page(url: str, session: requests.Session) -> BeautifulSoup:
    response = session.get(url, headers=HEADERS, timeout=20)
    response.raise_for_status()
    return BeautifulSoup(response.text, "lxml")


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


def crawl(max_pages: int = 2, delay_seconds: float = 2.0):
    all_jobs = []
    seen_urls = set()
    session = requests.Session()

    for page in range(1, max_pages + 1):
        url = f"{START_URL}?page={page}"
        print(f"Crawling: {url}")

        soup = fetch_page(url, session)
        jobs = parse_jobs(soup)

        for job in jobs:
            if job["url"] in seen_urls:
                continue

            seen_urls.add(job["url"])
            print(f"  Found: {job['title']}")
            all_jobs.append(job)

        time.sleep(delay_seconds)

    return all_jobs


if __name__ == "__main__":
    crawl(max_pages=2)
