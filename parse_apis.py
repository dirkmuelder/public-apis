#!/usr/bin/env python3
"""Parse public-apis README.md into structured JSON."""
import re, json, sys
from pathlib import Path

def parse_readme(path: str) -> list[dict]:
    text = Path(path).read_text(encoding="utf-8")
    apis = []
    current_category = None

    for line in text.splitlines():
        # Category heading (### Animals, ### Weather, ...)
        m = re.match(r"^###\s+(.+)", line)
        if m:
            current_category = m.group(1).strip()
            continue

        # Data row: | [Name](url) | desc | auth | https | cors |
        if not current_category:
            continue
        m = re.match(r"^\|\s*\[([^\]]+)\]\(([^)]+)\)\s*\|\s*([^|]*)\|\s*([^|]*)\|\s*([^|]*)\|\s*([^|]*)\|", line)
        if m:
            apis.append({
                "name":        m.group(1).strip(),
                "url":         m.group(2).strip(),
                "description": m.group(3).strip(),
                "auth":        m.group(4).strip(),
                "https":       m.group(5).strip(),
                "cors":        m.group(6).strip(),
                "category":    current_category,
            })

    return apis

if __name__ == "__main__":
    readme = Path(__file__).parent / "README.md"
    apis = parse_readme(readme)
    out = Path(__file__).parent / "apis.json"
    out.write_text(json.dumps(apis, indent=2, ensure_ascii=False))
    print(f"✓ {len(apis)} APIs parsed → {out}")
