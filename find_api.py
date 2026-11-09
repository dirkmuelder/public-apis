#!/usr/bin/env python3
"""CLI tool to search and filter APIs from apis_clean.json.

Usage:
  python find_api.py                        # show all categories
  python find_api.py weather                # search by keyword
  python find_api.py --free                 # only APIs with no auth
  python find_api.py --cors                 # only browser-usable APIs
  python find_api.py weather --free --cors  # combine filters
  python find_api.py --category Animals     # exact category
  python find_api.py --random               # random API for inspiration
  python find_api.py --stats                # show statistics
"""
import json
import random
import argparse
from pathlib import Path
from collections import Counter


DATA = Path(__file__).parent / "apis_clean.json"


def load() -> list[dict]:
    return json.loads(DATA.read_text(encoding="utf-8"))


def print_api(api: dict, idx: int | None = None) -> None:
    prefix = f"[{idx}] " if idx is not None else ""
    auth = api["auth"] or "none"
    cors = "✓ CORS" if api["cors"] == "Yes" else "✗ CORS"
    https = "🔒" if api["https"] == "Yes" else "  "
    print(f"{prefix}{https} {api['name']}")
    print(f"    {api['description']}")
    print(f"    {api['url']}")
    print(f"    Category: {api['category']} | Auth: {auth} | {cors}")
    print()


def cmd_stats(apis: list[dict]) -> None:
    categories = Counter(a["category"] for a in apis)
    auth_types = Counter(a["auth"] or "none" for a in apis)
    free = sum(1 for a in apis if not a["auth"])
    cors_ok = sum(1 for a in apis if a["cors"] == "Yes")
    https_ok = sum(1 for a in apis if a["https"] == "Yes")

    print(f"📊 API Statistics ({len(apis)} total)")
    print(f"   Free (no auth):  {free:4d}  ({free*100//len(apis)}%)")
    print(f"   CORS enabled:    {cors_ok:4d}  ({cors_ok*100//len(apis)}%)")
    print(f"   HTTPS:           {https_ok:4d}  ({https_ok*100//len(apis)}%)")
    print()
    print("📂 Categories:")
    for cat, count in categories.most_common():
        bar = "█" * (count // 5)
        print(f"   {cat:<30} {count:3d} {bar}")
    print()
    print("🔑 Auth types:")
    for auth, count in auth_types.most_common():
        print(f"   {auth:<20} {count:3d}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Search public APIs")
    parser.add_argument("query", nargs="?", help="keyword search (name, description, category)")
    parser.add_argument("--free", action="store_true", help="only APIs with no auth required")
    parser.add_argument("--cors", action="store_true", help="only CORS-enabled APIs (browser-usable)")
    parser.add_argument("--https", action="store_true", help="only HTTPS APIs")
    parser.add_argument("--category", "-c", help="exact category name (case-insensitive)")
    parser.add_argument("--random", "-r", action="store_true", help="show a random API")
    parser.add_argument("--stats", "-s", action="store_true", help="show statistics")
    parser.add_argument("--limit", "-n", type=int, default=20, help="max results (default 20)")
    args = parser.parse_args()

    apis = load()

    if args.stats:
        cmd_stats(apis)
        return

    if args.random:
        print_api(random.choice(apis))
        return

    if args.free:
        apis = [a for a in apis if not a["auth"]]
    if args.cors:
        apis = [a for a in apis if a["cors"] == "Yes"]
    if args.https:
        apis = [a for a in apis if a["https"] == "Yes"]
    if args.category:
        apis = [a for a in apis if a["category"].lower() == args.category.lower()]
    if args.query:
        q = args.query.lower()
        apis = [a for a in apis if
                q in a["name"].lower() or
                q in a["description"].lower() or
                q in a["category"].lower()]

    if not apis:
        print("No APIs found. Try broader search or fewer filters.")
        return

    total = len(apis)
    apis = apis[:args.limit]
    print(f"Found {total} APIs{f' (showing {len(apis)})' if total > len(apis) else ''}:\n")
    for i, api in enumerate(apis, 1):
        print_api(api, i)

    if total > args.limit:
        print(f"  … and {total - args.limit} more. Use --limit {total} to see all.")


if __name__ == "__main__":
    main()
