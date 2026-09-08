"""扫描 docs/ 与根目录 markdown 的相对链接与图片路径是否存在；CI 与本地验证共用。"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
FORBIDDEN = ("технический", "único", "18,561", "三轨")


def main() -> int:
    files = list((ROOT / "docs").glob("*.md")) + [
        ROOT / "README.md",
        ROOT / "CLAUDE.md",
    ]
    broken: list[str] = []
    for md in files:
        text = md.read_text(encoding="utf-8")
        for word in FORBIDDEN:
            if word in text:
                broken.append(f"{md.relative_to(ROOT)}: forbidden token {word!r}")
        for target in LINK_RE.findall(text):
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            path = target.split("#", 1)[0]
            if not path:
                continue
            if not (md.parent / path).exists():
                broken.append(f"{md.relative_to(ROOT)}: missing {target}")
    for line in broken:
        print(line)
    print(f"checked {len(files)} files, {len(broken)} problems")
    return 1 if broken else 0


if __name__ == "__main__":
    sys.exit(main())
