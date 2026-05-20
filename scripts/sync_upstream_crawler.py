#!/usr/bin/env python3
"""
Check for golang packages in rancher/vexhub that are not yet registered
in the upstream aquasecurity/vexhub-crawler crawler.yaml.

Outputs:
  - Sets GITHUB_OUTPUT has_new_entries=true|false
  - Writes new entries YAML to /tmp/new_entries.yaml  (when has_new_entries=true)
  - Writes a Markdown PR body to  /tmp/pr_body.md     (when has_new_entries=true)
"""

import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

import yaml

VEXHUB_BASE_URL = "https://github.com/rancher/vexhub"
UPSTREAM_CRAWLER_URL = (
    "https://raw.githubusercontent.com/aquasecurity/vexhub-crawler/main/crawler.yaml"
)
PKG_GOLANG_DIR = Path("pkg/golang")

NEW_ENTRIES_FILE = "/tmp/new_entries.yaml"
PR_BODY_FILE = "/tmp/pr_body.md"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def get_local_golang_packages() -> list[dict]:
    """Return all golang packages as a list of {namespace, name, url} dicts.

    Each package corresponds to a directory beneath pkg/golang/ that contains
    a scan.openvex.json file.  The namespace is the parent path and the name
    is the final path component, mirroring the format used in the upstream
    crawler.yaml.
    """
    packages: list[dict] = []

    for vex_file in sorted(PKG_GOLANG_DIR.rglob("scan.openvex.json")):
        rel_dir = vex_file.parent.relative_to(PKG_GOLANG_DIR)
        parts = rel_dir.parts

        if len(parts) < 2:
            # Need at least one namespace segment and a name
            continue

        namespace = "/".join(parts[:-1])
        name = parts[-1]
        url = f"{VEXHUB_BASE_URL}/tree/main/pkg/golang/{rel_dir}"

        packages.append({"namespace": namespace, "name": name, "url": url})

    return packages


def get_upstream_entries() -> set[tuple[str, str]]:
    """Fetch the upstream crawler.yaml and return the set of (namespace, name)
    pairs that already have a url pointing to rancher/vexhub."""

    req = urllib.request.Request(
        UPSTREAM_CRAWLER_URL,
        headers={"User-Agent": "rancher-vexhub-sync/1.0"},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = yaml.safe_load(resp.read().decode("utf-8"))
    except urllib.error.URLError as exc:
        print(f"ERROR: Could not fetch upstream crawler.yaml: {exc}", file=sys.stderr)
        sys.exit(1)

    entries: set[tuple[str, str]] = set()
    for entry in data.get("pkg", {}).get("golang", []):
        if VEXHUB_BASE_URL in entry.get("url", ""):
            entries.add((entry["namespace"], entry["name"]))

    return entries


def write_pr_body(new_entries: list[dict]) -> None:
    lines = [
        "## New Rancher VEX Hub Entries",
        "",
        "This PR adds the following new golang package entries from the "
        "[Rancher VEX Hub](https://github.com/rancher/vexhub):",
        "",
    ]
    for entry in new_entries:
        lines.append(f"- `{entry['namespace']}/{entry['name']}`")
    lines += [
        "",
        "_This PR was created automatically by the "
        "[Rancher VEX Hub sync workflow]"
        "(https://github.com/rancher/vexhub/actions)._",
    ]

    with open(PR_BODY_FILE, "w") as fh:
        fh.write("\n".join(lines) + "\n")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> int:
    if not PKG_GOLANG_DIR.is_dir():
        print(
            f"ERROR: {PKG_GOLANG_DIR} directory not found. "
            "Run this script from the root of the vexhub repository.",
            file=sys.stderr,
        )
        return 1

    local_packages = get_local_golang_packages()
    print(f"Local golang packages found   : {len(local_packages)}", file=sys.stderr)

    upstream_entries = get_upstream_entries()
    print(
        f"Upstream rancher/vexhub entries: {len(upstream_entries)}", file=sys.stderr
    )

    new_entries = [
        p
        for p in local_packages
        if (p["namespace"], p["name"]) not in upstream_entries
    ]
    print(f"New entries to add             : {len(new_entries)}", file=sys.stderr)

    has_new = "true" if new_entries else "false"

    # Write to GITHUB_OUTPUT when running inside GitHub Actions
    github_output = os.environ.get("GITHUB_OUTPUT", "")
    if github_output:
        with open(github_output, "a") as fh:
            fh.write(f"has_new_entries={has_new}\n")
    else:
        print(f"has_new_entries={has_new}")

    if new_entries:
        with open(NEW_ENTRIES_FILE, "w") as fh:
            yaml.dump(new_entries, fh, default_flow_style=False, allow_unicode=True)

        write_pr_body(new_entries)

        print("\nPackages not yet in upstream crawler.yaml:", file=sys.stderr)
        for entry in new_entries:
            print(f"  + {entry['namespace']}/{entry['name']}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
