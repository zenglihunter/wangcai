#!/usr/bin/env python3
"""Render the homepage post list and JSON-LD from data/posts.json."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POSTS_JSON = ROOT / "data" / "posts.json"
INDEX_HTML = ROOT / "index.html"
SITE_URL = "https://zenglihunter.github.io/wangcai"
POSTS_BEGIN = "<!--posts-begin-->"
POSTS_END = "<!--posts-end-->"
JSONLD_BEGIN = "<!--jsonld-begin-->"
JSONLD_END = "<!--jsonld-end-->"
TZ_OFFSET = "+08:00"


def build_cards(posts: list[dict]) -> str:
    cards = []
    for post in posts:
        tags_html = "".join(f"<span>#{tag}</span>" for tag in post.get("tags", []))
        published = post.get("published_at") or f"{post['date']} 00:00"
        updated = post.get("updated_at") or published
        published_iso = to_iso(published)
        updated_iso = to_iso(updated)
        card = f"""        <article class=\"post-card\" itemscope itemtype=\"https://schema.org/BlogPosting\">
          <div class=\"post-meta\">
            <time datetime=\"{published_iso}\" itemprop=\"datePublished\">发布：{published}</time>
            <span itemprop=\"dateModified\" data-iso=\"{updated_iso}\">更新：{updated}</span>
            <meta itemprop=\"author\" content=\"旺财\">
            <meta itemprop=\"publisher\" content=\"旺财日志\">
          </div>
          <h3 itemprop=\"headline\"><a href=\"{post['url']}\" itemprop=\"url mainEntityOfPage\">{post['title']}</a></h3>
          <p itemprop=\"description\">{post['summary']}</p>
          <div class=\"post-tags\">{tags_html}</div>
        </article>"""
        cards.append(card)
    return "\n".join(cards)


def build_jsonld(posts: list[dict]) -> str:
    data = {
        "@context": "https://schema.org",
        "@type": "Blog",
        "name": "旺财日志",
        "url": SITE_URL,
        "inLanguage": "zh-CN",
        "blogPost": [
            {
                "@type": "BlogPosting",
                "headline": post["title"],
                "datePublished": to_iso(post.get("published_at") or f"{post['date']} 00:00"),
                "dateModified": to_iso(post.get("updated_at") or f"{post['date']} 00:00"),
                "description": post["summary"],
                "url": f"{SITE_URL}/{post['url']}",
                "author": {"@type": "Person", "name": "旺财"}
            }
            for post in posts
        ]
    }
    return json.dumps(data, ensure_ascii=False, indent=2)


def to_iso(ts: str) -> str:
    try:
        dt = datetime.strptime(ts, "%Y-%m-%d %H:%M")
        return dt.strftime("%Y-%m-%dT%H:%M:00") + TZ_OFFSET
    except ValueError:
        return ts


def inject_between(mark_begin: str, mark_end: str, original: str, payload: str) -> str:
    if mark_begin not in original or mark_end not in original:
        raise RuntimeError("Markers not found in index.html")
    start = original.index(mark_begin) + len(mark_begin)
    end = original.index(mark_end)
    before = original[:start]
    after = original[end:]
    # ensure indentation keeps 8 spaces (matching <div> children)
    payload_block = "\n" + payload + "\n        "
    return before + payload_block + after


def render() -> None:
    posts = json.loads(POSTS_JSON.read_text(encoding="utf-8"))
    html = INDEX_HTML.read_text(encoding="utf-8")
    cards = build_cards(posts)
    html = inject_between(POSTS_BEGIN, POSTS_END, html, cards)
    jsonld = build_jsonld(posts)
    html = inject_between(JSONLD_BEGIN, JSONLD_END, html, jsonld)
    INDEX_HTML.write_text(html, encoding="utf-8")
    print("✅ Homepage updated with", len(posts), "posts")


if __name__ == "__main__":
    render()
