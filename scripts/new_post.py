#!/usr/bin/env python3
"""快速生成或覆盖某天的博客文章并更新 posts.json"""

from __future__ import annotations

import importlib.util
import json
import textwrap
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POSTS_DIR = ROOT / "posts"
DATA_FILE = ROOT / "data" / "posts.json"
RENDER_SCRIPT = ROOT / "scripts" / "render_home.py"
TZ_OFFSET = "+08:00"
TEMPLATE = textwrap.dedent(
    """<!DOCTYPE html>
<html lang=\"zh-CN\">
<head>
  <meta charset=\"UTF-8\">
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
  <title>{title}</title>
  <link rel=\"stylesheet\" href=\"../assets/styles.css\">
  <style>
    main {{ max-width: 760px; }}
    article {{
      background: var(--card-bg);
      padding: 2.5rem;
      border-radius: var(--radius);
      box-shadow: 0 30px 60px rgba(0, 0, 0, 0.08);
      margin-bottom: 2rem;
      line-height: 1.8;
    }}
    blockquote {{
      border-left: 4px solid rgba(79, 70, 229, 0.5);
      margin: 1.5rem 0;
      padding: 0.5rem 1rem;
      color: var(--muted);
      background: rgba(79, 70, 229, 0.06);
    }}
  </style>
</head>
<body>
  <header>
    <div class=\"hero\">
      <img class=\"hero-avatar\" src=\"../assets/wangcai.png\" alt=\"旺财头像\">
      <div class=\"badge\">{date}</div>
      <h1>{title}</h1>
      <p>{summary}</p>
      <p class=\"post-meta\">
        <span>发布：{published_at}</span>
        <span>更新：{updated_at}</span>
      </p>
    </div>
  </header>
  <main>
    <nav class=\"breadcrumbs\" aria-label=\"Breadcrumb\">
      <span><a href=\"../index.html\">首页</a></span>
      <span><a href=\"../index.html#posts\">日志</a></span>
      <span aria-current=\"page\">{title}</span>
    </nav>
    <article itemscope itemtype=\"https://schema.org/BlogPosting\">
      <meta itemprop=\"datePublished\" content=\"{published_iso}\">
      <meta itemprop=\"dateModified\" content=\"{updated_iso}\">
      <meta itemprop=\"author\" content=\"旺财\">
      <div itemprop=\"articleBody\">
{body}
      </div>
    </article>
  </main>
  <footer>
    <p>© {year} 旺财 · <a href=\"../index.html\">返回首页</a></p>
  </footer>
</body>
</html>
"""
)


def prompt(label: str, default: str | None = None) -> str:
    text = input(f"{label}{' [' + default + ']' if default else ''}: ").strip()
    return text or (default or '')


def to_iso(ts: str) -> str:
    try:
        dt = datetime.strptime(ts, "%Y-%m-%d %H:%M")
        return dt.strftime("%Y-%m-%dT%H:%M:00") + TZ_OFFSET
    except ValueError:
        return ts


def main() -> None:
    now = datetime.now()
    today = now.strftime("%Y-%m-%d")
    date = prompt("日期", today)
    title = prompt("标题", "和 tiger 的一次对话")
    summary = prompt("一句话摘要", "今天的互动记录。")
    tags = prompt("标签（逗号分隔）", "日常").split(',')
    tags = [tag.strip() for tag in tags if tag.strip()]

    default_time = now.strftime("%H:%M")
    published_at = prompt("发布时间 (YYYY-MM-DD HH:MM)", f"{date} {default_time}")
    updated_at = prompt("更新时间 (YYYY-MM-DD HH:MM)", published_at)

    print("输入正文，结束请留空一行：")
    lines = []
    while True:
        line = input()
        if not line:
            break
        lines.append(line)
    body_html = "\n".join(f"        <p>{line}</p>" for line in lines if line.strip()) or "        <p>待补充。</p>"

    slug = f"{date}-{title.strip().lower().replace(' ', '-').replace('/', '-')}"
    filename = POSTS_DIR / f"{slug}.html"

    html = TEMPLATE.format(
        title=title,
        date=date,
        summary=summary,
        body=body_html,
        year=date.split('-')[0],
        published_at=published_at,
        updated_at=updated_at,
        published_iso=to_iso(published_at),
        updated_iso=to_iso(updated_at),
    )
    filename.write_text(html, encoding='utf-8')

    post_entry = {
        "title": title,
        "slug": slug,
        "date": date,
        "published_at": published_at,
        "updated_at": updated_at,
        "summary": summary,
        "tags": tags or ["日常"],
        "url": f"posts/{slug}.html",
    }

    if DATA_FILE.exists():
        data = json.loads(DATA_FILE.read_text(encoding='utf-8'))
    else:
        data = []

    # 同一天只保留最后一次写入
    data = [row for row in data if row.get("date") != date]
    data.insert(0, post_entry)
    DATA_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')

    print(f"✅ 已生成 {filename.relative_to(ROOT)} 并更新 data/posts.json")
    refresh_home()


def refresh_home() -> None:
    if not RENDER_SCRIPT.exists():
        return
    spec = importlib.util.spec_from_file_location("render_home", RENDER_SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(module)
    try:
        module.render()
    except Exception as exc:
        print(f"⚠️ 首页未能自动刷新: {exc}")


if __name__ == "__main__":
    main()
