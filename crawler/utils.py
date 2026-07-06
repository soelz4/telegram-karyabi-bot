from urllib.parse import urlsplit, urlunsplit

import requests
from bs4 import BeautifulSoup

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
    response = session.get(url, headers=headers or HEADERS, timeout=20)
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
