#!/usr/bin/env python3
"""Surface today's GitHub Trending repos that aren't another AI/agent wrapper."""

import argparse
import datetime
import re
from pathlib import Path

import requests
from bs4 import BeautifulSoup

TRENDING_URL = "https://github.com/trending"

AI_KEYWORDS = re.compile(
    r"\b(ai|artificial[- ]intelligence|agent|agentic|llm|gpt|chatgpt|claude|copilot|"
    r"langchain|langgraph|rag|chatbot|machine[- ]learning|\bml\b|neural|transformer|"
    r"prompt|genai|gen-ai|openai|anthropic|gemini|diffusion|stable[- ]diffusion|"
    r"embedding|vector[- ]db|autonomous[- ]agent|mcp)\b",
    re.IGNORECASE,
)


def fetch_trending(period: str, language: str | None) -> list[dict]:
    params = {"since": period}
    if language:
        params["l"] = language
    resp = requests.get(
        TRENDING_URL,
        params=params,
        timeout=15,
        headers={"User-Agent": "anti-trending/0.1 (https://github.com)"},
    )
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    repos = []
    for article in soup.select("article.Box-row"):
        link = article.select_one("h2 a")
        if not link:
            continue
        full_name = link["href"].strip("/")
        desc_el = article.select_one("p")
        description = desc_el.get_text(strip=True) if desc_el else ""
        lang_el = article.select_one("[itemprop='programmingLanguage']")
        lang = lang_el.get_text(strip=True) if lang_el else ""
        star_today_el = article.select_one("span.d-inline-block.float-sm-right")
        stars_today = star_today_el.get_text(strip=True) if star_today_el else ""

        repos.append(
            {
                "full_name": full_name,
                "description": description,
                "language": lang,
                "stars_today": stars_today,
                "url": f"https://github.com/{full_name}",
            }
        )
    return repos


def is_ai_slop(repo: dict) -> bool:
    text = f"{repo['full_name']} {repo['description']}"
    return bool(AI_KEYWORDS.search(text))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--since", choices=["daily", "weekly", "monthly"], default="daily")
    parser.add_argument("--language", default=None, help="Filter by language, e.g. python")
    parser.add_argument("--save", action="store_true", help="Save results to a dated markdown file")
    args = parser.parse_args()

    repos = fetch_trending(args.since, args.language)
    weird = [r for r in repos if not is_ai_slop(r)]
    ai = [r for r in repos if is_ai_slop(r)]

    print(f"GitHub Trending ({args.since}): {len(repos)} repos total")
    print(f"Filtered out {len(ai)} AI/agent wrappers. {len(weird)} weird & unique repos left:\n")

    for r in weird:
        stars_today = f" (+{r['stars_today']})" if r["stars_today"] else ""
        lang = f"[{r['language']}] " if r["language"] else ""
        print(f"- {lang}{r['full_name']}{stars_today}")
        if r["description"]:
            print(f"  {r['description']}")
        print(f"  {r['url']}\n")

    if args.save:
        today = datetime.date.today().isoformat()
        out_dir = Path(__file__).parent / "results"
        out_dir.mkdir(exist_ok=True)
        out_path = out_dir / f"{today}-{args.since}.md"
        lines = [
            f"# Anti-Trending - {today} ({args.since})\n",
            f"Filtered {len(ai)} AI/agent repos out of {len(repos)} trending. {len(weird)} left.\n",
        ]
        for r in weird:
            stars_today = f" (+{r['stars_today']})" if r["stars_today"] else ""
            lang = f"`{r['language']}` " if r["language"] else ""
            lines.append(f"## {lang}[{r['full_name']}]({r['url']}){stars_today}\n")
            if r["description"]:
                lines.append(f"{r['description']}\n")
        out_path.write_text("\n".join(lines), encoding="utf-8")
        print(f"Saved to {out_path}")


if __name__ == "__main__":
    main()
