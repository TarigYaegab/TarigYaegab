#!/usr/bin/env python3
"""Builds a neofetch-style GitHub profile README.

Usage:
    python build_readme.py            # uses GH_USER env var or USERNAME below
Needs: ascii.txt (your photo as ASCII) in the same folder. No pip packages.
"""
import json
import os
import urllib.request
from collections import Counter
from datetime import datetime, timezone

# ============ EDIT THESE ============
USER = os.environ.get("GH_USER", "USERNAME")   # your GitHub username
NAME = "tarig"
ROLE = "Flutter Developer"
FOCUS = "Mobile Apps, ML (learning)"
EMAIL = "your@email.com"
PROJECTS = [
    ("Bill App", "Flutter POS for retail shops"),
    ("Al-Joun", "Static construction website"),
    ("nawakAI", "ML/DL from scratch"),
]
# ====================================

TOKEN = os.environ.get("GITHUB_TOKEN")
WIDTH = 46   # width of the info column
GAP = 4      # spaces between ASCII art and info


def api(path):
    headers = {"Accept": "application/vnd.github+json"}
    if TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"
    req = urllib.request.Request("https://api.github.com" + path, headers=headers)
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r)


def get_stats():
    user = api(f"/users/{USER}")
    repos = api(f"/users/{USER}/repos?per_page=100&type=owner")
    stars = sum(r["stargazers_count"] for r in repos)
    langs = Counter(r["language"] for r in repos if r["language"])
    try:
        commits = api(f"/search/commits?q=author:{USER}&per_page=1")["total_count"]
    except Exception:
        commits = "?"
    created = datetime.fromisoformat(user["created_at"].replace("Z", "+00:00"))
    days = (datetime.now(timezone.utc) - created).days
    return {
        "repos": user["public_repos"],
        "followers": user["followers"],
        "stars": stars,
        "commits": commits,
        "uptime": f"{days // 30} months, {days % 30} days",
        "langs": ", ".join(l for l, _ in langs.most_common(3)) or "-",
    }


def dots(label, value):
    """'. Label: ........... value' padded to WIDTH."""
    left = f". {label}: "
    fill = max(2, WIDTH - len(left) - len(value) - 1)
    return f"{left}{'.' * fill} {value}"


def header(title):
    return f"{title} " + "─" * max(2, WIDTH - len(title) - 1)


def build_info(s):
    lines = [
        header(f"{NAME}@github"),
        dots("Role", ROLE),
        dots("Focus", FOCUS),
        dots("Languages", s["langs"]),
        dots("Uptime", s["uptime"]),
        "",
        header("Projects"),
        *[dots(n, d) for n, d in PROJECTS],
        "",
        header("Contact"),
        dots("GitHub", f"github.com/{USER}"),
        dots("Email", EMAIL),
        "",
        header("GitHub Stats"),
        dots("Repos", str(s["repos"])) + "  ",
        dots("Commits", str(s["commits"])),
        dots("Stars", str(s["stars"])),
        dots("Followers", str(s["followers"])),
    ]
    return lines


def merge(ascii_lines, info_lines):
    art_w = max((len(l) for l in ascii_lines), default=0)
    total = max(len(ascii_lines), len(info_lines))
    a_off = (total - len(ascii_lines)) // 2
    i_off = (total - len(info_lines)) // 2
    out = []
    for n in range(total):
        a = ascii_lines[n - a_off] if 0 <= n - a_off < len(ascii_lines) else ""
        i = info_lines[n - i_off] if 0 <= n - i_off < len(info_lines) else ""
        out.append((a.ljust(art_w) + " " * GAP + i).rstrip())
    return "\n".join(out)


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(here, "ascii_tarig.txt"), encoding="utf-8") as f:
        ascii_lines = f.read().rstrip("\n").split("\n")

    body = merge(ascii_lines, build_info(get_stats()))
    readme = f"<div align=\"center\">\n\n```text\n{body}\n```\n\n</div>\n"

    with open(os.path.join(here, "README.md"), "w", encoding="utf-8") as f:
        f.write(readme)
    print("README.md updated")


if __name__ == "__main__":
    main()
