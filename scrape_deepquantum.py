from __future__ import annotations

from pathlib import Path

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://deepquantum.turingq.com/2024/07/10/%e9%87%8f%e5%ad%90%e8%ae%a1%e7%ae%97%e5%9f%ba%e7%a1%80/"
OUTPUT_PATH = Path("deepquantum_algorithm_cases.md")

def fetch_cases(url: str = BASE_URL):
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    content = soup.select_one("div.entry-content")
    cases = []
    for heading in content.find_all("h3"):
        name = heading.get_text(strip=True)
        paragraph = heading.find_next_sibling(
            lambda tag: tag.name == "p" and tag.get_text(strip=True)
        )
        description = paragraph.get_text(strip=True) if paragraph else ""
        cases.append({
            "name": name,
            "description": description,
            "code_link": url,
        })
    return cases


def render_markdown_table(cases):
    lines = ["| 算法名称 | 算法简介 | 代码链接 |", "| --- | --- | --- |"]
    for case in cases:
        lines.append(
            f"| {case['name']} | {case['description']} | {case['code_link']} |"
        )
    return "\n".join(lines)


def main():
    cases = fetch_cases()
    table = render_markdown_table(cases)
    OUTPUT_PATH.write_text(table, encoding="utf-8")


if __name__ == "__main__":
    main()
