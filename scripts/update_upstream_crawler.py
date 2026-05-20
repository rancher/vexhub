#!/usr/bin/env python3
"""
Insert new golang entries into the upstream aquasecurity/vexhub-crawler
crawler.yaml.

Usage:
    python3 update_upstream_crawler.py <crawler.yaml> <new_entries.yaml>
"""

import sys
from pathlib import Path

import yaml


def load_yaml(path: Path) -> object:
    with open(path) as fh:
        return yaml.safe_load(fh)


def main() -> int:
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <crawler.yaml> <new_entries.yaml>")
        return 1

    crawler_path = Path(sys.argv[1])
    new_entries_path = Path(sys.argv[2])

    data = load_yaml(crawler_path)
    new_entries = load_yaml(new_entries_path) or []

    if not new_entries:
        print("No new entries to add.")
        return 0

    golang_entries: list = data.setdefault("pkg", {}).setdefault("golang", [])

    # Build a set of existing (namespace, name) pairs for de-duplication
    existing: set[tuple[str, str]] = {
        (e["namespace"], e["name"]) for e in golang_entries
    }

    added = 0
    for entry in new_entries:
        key = (entry["namespace"], entry["name"])
        if key not in existing:
            golang_entries.append(entry)
            existing.add(key)
            added += 1

    print(f"Added {added} new entry/entries to {crawler_path}.")

    with open(crawler_path, "w") as fh:
        yaml.dump(data, fh, default_flow_style=False, allow_unicode=True, sort_keys=False)

    return 0


if __name__ == "__main__":
    sys.exit(main())
