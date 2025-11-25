from __future__ import annotations

from pathlib import Path
import re
from typing import Iterable

import requests
from bs4 import BeautifulSoup

BASE_LIST_URL = "https://deepquantum.turingq.com/news/"
OUTPUT_PATH = Path("deepquantum_algorithm_cases.md")


def _get_soup(url: str, session: requests.Session) -> BeautifulSoup:
    response = session.get(url)
    response.raise_for_status()
    return BeautifulSoup(response.text, "html.parser")


def fetch_algorithm_links(list_url: str, session: requests.Session) -> list[str]:
    """Collect algorithm article links from the news page."""

    soup = _get_soup(list_url, session)
    content = soup.select_one("div.entry-content")
    if content is None:
        return []

    links: list[str] = []
    seen: set[str] = set()
    for anchor in content.find_all("a", href=True):
        href: str = anchor["href"]
        if re.match(r"https://deepquantum\.turingq\.com/20\d{2}/", href) and href not in seen:
            seen.add(href)
            links.append(href)
    return links


def _first_paragraph_text(container: BeautifulSoup | None) -> str:
    if container is None:
        return ""

    for paragraph in container.find_all("p"):
        text = paragraph.get_text(strip=True)
        if text:
            return text
    return ""


def fetch_case(url: str, session: requests.Session) -> dict[str, str]:
    soup = _get_soup(url, session)
    name = soup.select_one("h1.page-title, h1.entry-title, h1.wp-block-heading")
    content = soup.select_one("div.entry-content")
    description = _first_paragraph_text(content)
    return {
        "name": name.get_text(strip=True) if name else url,
        "description": description,
        "code_link": url,
    }


def fetch_cases(list_url: str = BASE_LIST_URL) -> Iterable[dict[str, str]]:
    with requests.Session() as session:
        links = fetch_algorithm_links(list_url, session)
        for link in links:
            yield fetch_case(link, session)


def render_markdown_table(cases: Iterable[dict[str, str]]) -> str:
    lines = ["| 算法名称 | 算法简介 | 代码链接 |", "| --- | --- | --- |"]
    for case in cases:
        lines.append(
            f"| {case['name']} | {case['description']} | {case['code_link']} |"
        )
    return "\n".join(lines)


def main():
    cases = list(fetch_cases())
    table = render_markdown_table(cases)
    OUTPUT_PATH.write_text(table, encoding="utf-8")


if __name__ == "__main__":
    main()
