import time
from urllib.parse import urljoin

import requests

from crawler.utils import HEADERS, clean_text, html_to_text, unique

BASE_URL = "https://jobvision.ir"
API_BASE_URL = "https://candidateapi.jobvision.ir/api/v1/JobPost"

JOBVISION_HEADERS = {
    **HEADERS,
    "Origin": BASE_URL,
    "Referer": f"{BASE_URL}/jobs",
}


def title_fa(value) -> str:
    return clean_text((value or {}).get("titleFa") or (value or {}).get("title") or "")


def fetch_jobs_page(page: int, session: requests.Session, page_size: int = 20):
    response = session.post(
        f"{API_BASE_URL}/List",
        headers=JOBVISION_HEADERS,
        json={"requestedPage": page, "sortBy": 0, "pageSize": page_size},
        timeout=20,
    )
    response.raise_for_status()
    data = response.json()
    if not data.get("isSuccess"):
        raise RuntimeError(data.get("message") or "Jobvision list request failed")
    return data["data"]["jobPosts"]


def fetch_job_detail(job_id: int, session: requests.Session):
    response = session.get(
        f"{API_BASE_URL}/Detail",
        headers=JOBVISION_HEADERS,
        params={"jobPostId": job_id},
        timeout=20,
    )
    response.raise_for_status()
    data = response.json()
    if not data.get("isSuccess"):
        raise RuntimeError(data.get("message") or "Jobvision detail request failed")
    return data["data"]


def parse_job(job: dict):
    company = job.get("company") or {}
    location = job.get("location") or {}
    activation_time = job.get("activationTime") or {}

    return {
        "jobvision_id": job["id"],
        "title": clean_text(job.get("title")),
        "company": clean_text(company.get("nameFa") or company.get("nameEn")),
        "location": get_location(location),
        "published": title_or_value(activation_time, "beautifyFa"),
        "published_at": title_or_value(activation_time, "date"),
        "salary": title_fa(job.get("salary")),
        "experience": title_fa(job.get("seniorityLevel")),
        "work_type": title_fa(job.get("workType")),
        "industry": title_fa(job.get("industry")),
        "benefits": "\n".join(get_titles(job.get("benefits"))),
        "tags": "\n".join(get_tags(job)),
        "url": urljoin(BASE_URL, f"/jobs/{job['id']}"),
        "job_description": "",
        "company_description": "",
    }


def title_or_value(value: dict, key: str) -> str:
    return clean_text((value or {}).get(key))


def get_location(location: dict) -> str:
    parts = [
        title_fa(location.get("province")),
        title_fa(location.get("city")),
        title_fa(location.get("region")),
    ]
    return "، ".join(part for part in parts if part)


def get_titles(items) -> list[str]:
    return unique(title_fa(item) for item in items or [])


def get_tags(job: dict) -> list[str]:
    tags = []

    for source in (
        job.get("skills"),
        job.get("jobCategories"),
        job.get("softwareRequirements"),
        job.get("languageRequirements"),
    ):
        for title in get_titles(source):
            if title not in tags:
                tags.append(title)

    return tags


def parse_job_details(detail: dict):
    return {
        "job_description": html_to_text(detail.get("description")),
        "company_description": get_company_description(detail.get("company") or {}),
        "tags": "\n".join(get_tags(detail)),
    }


def get_company_description(company: dict) -> str:
    parts = [
        title_fa(company.get("industries", [{}])[0]) if company.get("industries") else "",
        title_fa(company.get("size")),
        title_fa(company.get("ownershipType")),
        title_fa(company.get("companyType")),
        html_to_text((company.get("description") or {}).get("titleFa")),
        html_to_text((company.get("shortDescription") or {}).get("titleFa")),
        html_to_text((company.get("productsOrServices") or {}).get("titleFa")),
    ]

    unique_parts = []
    for part in parts:
        if part and part not in unique_parts:
            unique_parts.append(part)

    return "\n".join(unique_parts)


def enrich_job_details(job: dict, session: requests.Session):
    detail = fetch_job_detail(job["jobvision_id"], session)
    return {**job, **parse_job_details(detail)}


def crawl(max_pages: int = 1, delay_seconds: float = 2.0, start_page: int = 2):
    all_jobs = []
    seen_urls = set()
    session = requests.Session()

    for page in range(start_page, start_page + max_pages):
        url = f"{BASE_URL}/jobs?page={page}"
        print(f"Crawling: {url}")

        jobs = fetch_jobs_page(page, session)
        for job_data in jobs:
            job = parse_job(job_data)
            if job["url"] in seen_urls:
                continue

            seen_urls.add(job["url"])
            print(f"  Fetching detail: {job['title']}")
            all_jobs.append(enrich_job_details(job, session))
            time.sleep(delay_seconds)

        time.sleep(delay_seconds)

    return all_jobs
