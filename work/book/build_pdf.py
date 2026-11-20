"""把 docs/book/ 各章合并为单个 HTML，再用 Chrome headless 打印为 PDF。

用法：uv run --with markdown python work/book/build_pdf.py
"""

import re
import subprocess
import sys
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parents[2]
BOOK = ROOT / "docs" / "book"
OUT_DIR = Path(__file__).resolve().parent
HTML = OUT_DIR / "embodied-data-pipeline-book.html"
PDF = OUT_DIR / "embodied-data-pipeline-book.pdf"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

ORDER = ["README.md", "00-preface.md"] + sorted(
    p.name for p in BOOK.glob("[0-9][0-9]-*.md") if not p.name.startswith("00-")
) + ["appendix.md"]

CSS = """
@page { size: A4; margin: 18mm 16mm; }
body { font-family: "PingFang SC", "Hiragino Sans GB", "Noto Sans CJK SC", sans-serif;
       font-size: 10.5pt; line-height: 1.65; color: #1a1a1a; }
h1 { font-size: 20pt; border-bottom: 2px solid #333; padding-bottom: 4px; margin-top: 0; }
h2 { font-size: 14pt; margin-top: 1.4em; border-bottom: 1px solid #ccc; }
h3 { font-size: 12pt; margin-top: 1.1em; }
table { border-collapse: collapse; width: 100%; margin: 0.6em 0; font-size: 9pt; page-break-inside: auto; }
th, td { border: 1px solid #bbb; padding: 3px 6px; vertical-align: top; }
th { background: #f0f0f0; }
tr { page-break-inside: avoid; }
pre { background: #f6f6f6; border: 1px solid #ddd; padding: 8px; font-size: 8.5pt;
      white-space: pre-wrap; page-break-inside: avoid; }
code { font-family: "SF Mono", Menlo, monospace; font-size: 0.92em; }
img { max-width: 100%; display: block; margin: 0.6em auto; }
blockquote { color: #555; border-left: 3px solid #ccc; margin-left: 0; padding-left: 10px; }
.chapter { page-break-before: always; }
.chapter:first-child { page-break-before: avoid; }
"""


def main() -> int:
    md = markdown.Markdown(extensions=["tables", "fenced_code"])
    parts = []
    for name in ORDER:
        text = (BOOK / name).read_text(encoding="utf-8")
        # 章节间互链在合并版里没有意义，去掉 .md 链接只留文字；图片保持相对路径（base 指向 docs/book/）
        text = re.sub(r"(?<!!)\[([^\]]+)\]\(([^)]+\.md)(#[^)]*)?\)", r"\1", text)
        parts.append(f'<section class="chapter">{md.convert(text)}</section>')
        md.reset()
    html = (
        '<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">'
        f'<base href="{BOOK.as_uri()}/"><title>具身数据管线：从采集到回流</title>'
        f"<style>{CSS}</style></head><body>{''.join(parts)}</body></html>"
    )
    HTML.write_text(html, encoding="utf-8")
    subprocess.run(
        [CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
         "--allow-file-access-from-files", f"--print-to-pdf={PDF}", HTML.as_uri()],
        check=True, capture_output=True,
    )
    print(PDF, PDF.stat().st_size)
    return 0


if __name__ == "__main__":
    sys.exit(main())
