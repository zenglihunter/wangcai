#!/usr/bin/env python3
"""快速生成一篇博客文章并更新 posts.json"""

from __future__ import annotations

import json
import textwrap
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POSTS_DIR = ROOT / "posts"
DATA_FILE = ROOT / "data" / "posts.json"
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
    .back-link {{ display: inline-block; margin-bottom: 1rem; }}
  </style>
</head>
<body>
  <header>
    <div class=\"hero\">
      <div class=\"badge\">{date}</div>
      <h1>{title}</h1>
      <p>{summary}</p>
    </div>
  </header>
  <main>
    <a class=\"back-link\" href=\"../index.html\">← 返回主页</a>
    <article>
{body}
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


def main() -> None:
    today = datetime.now().strftime("%Y-%m-%d")
    date = prompt("日期", today)
    title = prompt("标题", "和 tiger 的一次对话")
    summary = prompt("一句话摘要", "今天的互动记录。")
    tags = prompt("标签（逗号分隔）", "日常").split(',')
    tags = [tag.strip() for tag in tags if tag.strip()]

    print("输入正文，结束请留空一行：")
    lines = []
    while True:
        line = input()
        if not line:
            break
        lines.append(line)
    body_html = "\n".join(f"      <p>{line}</p>" for line in lines if line.strip())

    slug = f"{date}-{title.strip().lower().replace(' ', '-').replace('/', '-') }"
    filename = POSTS_DIR / f"{slug}.html"

    html = TEMPLATE.format(title=title, date=date, summary=summary, body=body_html or "      <p>待补充。</p>", year=date.split('-')[0])
    filename.write_text(html, encoding='utf-8')

    post_entry = {
        "title": title,
        "slug": slug,
        "date": date,
        "summary": summary,
        "tags": tags or ["日常"],
        "url": f"posts/{slug}.html",
    }

    if DATA_FILE.exists():
        data = json.loads(DATA_FILE.read_text(encoding='utf-8'))
    else:
        data = []
    data.insert(0, post_entry)
    DATA_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')

    print(f"✅ 已生成 {filename.relative_to(ROOT)} 并更新 data/posts.json")


if __name__ == "__main__":
    main()
