#!/usr/bin/env python3
"""
Pull GitHub contribution/repo data via GraphQL+REST and render stats SVGs.
Uses only the Python standard library. Requires GITHUB_TOKEN and GH_LOGIN env vars.
"""
import os
import json
import urllib.request
from datetime import datetime, timedelta, timezone

TOKEN = os.environ["GITHUB_TOKEN"]
LOGIN = os.environ["GH_LOGIN"]
API = "https://api.github.com/graphql"

RAMP = " .`:-=+*cs#%@"
BG = "#0d1117"
FG = "#c9d1d9"
ACCENT = "#58a6ff"
DIM = "#8b949e"


def gql(query: str, variables: dict) -> dict:
    body = json.dumps({"query": query, "variables": variables}).encode()
    req = urllib.request.Request(
        API,
        data=body,
        headers={
            "Authorization": f"Bearer {TOKEN}",
            "Content-Type": "application/json",
            "User-Agent": LOGIN,
        },
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


def get_window():
    now = datetime.now(timezone.utc)
    to = now.replace(hour=23, minute=59, second=59, microsecond=0)
    frm = (to - timedelta(days=364)).replace(hour=0, minute=0, second=0)
    return frm.isoformat(), to.isoformat()


QUERY = """
query($login: String!, $from: DateTime!, $to: DateTime!) {
  user(login: $login) {
    contributionsCollection(from: $from, to: $to) {
      contributionCalendar {
        totalContributions
        weeks {
          contributionDays { date contributionCount }
        }
      }
    }
    repositories(first: 100, privacy: PUBLIC, isFork: false, ownerAffiliations: OWNER) {
      nodes {
        name
        languages(first: 5, orderBy: {field: SIZE, direction: DESC}) {
          edges { size node { name color } }
        }
      }
    }
  }
}
"""


def fetch():
    frm, to = get_window()
    data = gql(QUERY, {"login": LOGIN, "from": frm, "to": to})
    return data["data"]["user"]


def flatten_days(collection):
    days = []
    for week in collection["contributionCalendar"]["weeks"]:
        for d in week["contributionDays"]:
            days.append((d["date"], d["contributionCount"]))
    return days


def compute_streaks(days):
    cur = longest = 0
    cur_start = longest_start = longest_end = None
    running_start = None
    today = datetime.now(timezone.utc).date().isoformat()

    for date, count in days:
        if count > 0:
            if running_start is None:
                running_start = date
            cur += 1
            if cur > longest:
                longest = cur
                longest_start = running_start
                longest_end = date
        else:
            cur = 0
            running_start = None

    # trailing current streak (must include today or yesterday)
    trailing = 0
    trailing_start = None
    for date, count in reversed(days):
        if count > 0:
            trailing += 1
            trailing_start = date
        else:
            if date == today:
                continue
            break

    return {
        "current": trailing,
        "current_start": trailing_start,
        "longest": longest,
        "longest_start": longest_start,
        "longest_end": longest_end,
    }


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def svg_wrap(width, height, body, title=""):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}">\n'
        f'<rect width="100%" height="100%" fill="{BG}" rx="6"/>\n'
        f'<style>text{{font-family:\'JetBrains Mono\',\'DejaVu Sans Mono\',monospace}}</style>\n'
        f'{body}\n</svg>'
    )


def gen_hero_stats(total, weekly_counts, out_path):
    w, h = 480, 140
    body = [f'<text x="20" y="40" font-size="14" fill="{DIM}">total contributions</text>']
    body.append(f'<text x="20" y="75" font-size="36" fill="{FG}" font-weight="bold">{total:,}</text>')

    # sparkline over last 12 weeks
    spark = weekly_counts[-12:]
    max_v = max(spark) if spark and max(spark) > 0 else 1
    bar_w = 14
    gap = 6
    base_y = 130
    max_bar_h = 40
    x = 260
    for v in spark:
        bh = int((v / max_v) * max_bar_h) if max_v else 0
        bh = max(bh, 2)
        body.append(f'<rect x="{x}" y="{base_y - bh}" width="{bar_w}" height="{bh}" fill="{ACCENT}" rx="2"/>')
        x += bar_w + gap
    body.append(f'<text x="260" y="20" font-size="11" fill="{DIM}">last 12 weeks</text>')

    with open(out_path, "w") as f:
        f.write(svg_wrap(w, h, "\n".join(body)))


def gen_streak(streaks, out_path):
    w, h = 480, 140
    body = [f'<text x="20" y="35" font-size="14" fill="{DIM}">current streak</text>']
    body.append(f'<text x="20" y="72" font-size="30" fill="{ACCENT}" font-weight="bold">{streaks["current"]} days</text>')
    if streaks["current_start"]:
        body.append(f'<text x="20" y="92" font-size="11" fill="{DIM}">since {streaks["current_start"]}</text>')

    body.append(f'<text x="250" y="35" font-size="14" fill="{DIM}">longest streak</text>')
    body.append(f'<text x="250" y="72" font-size="30" fill="{FG}" font-weight="bold">{streaks["longest"]} days</text>')
    if streaks["longest_start"]:
        body.append(f'<text x="250" y="92" font-size="11" fill="{DIM}">{streaks["longest_start"]} to {streaks["longest_end"]}</text>')

    with open(out_path, "w") as f:
        f.write(svg_wrap(w, h, "\n".join(body)))


def gen_langs(repos, out_path):
    totals = {}
    colors = {}
    for r in repos:
        for edge in r["languages"]["edges"]:
            name = edge["node"]["name"]
            totals[name] = totals.get(name, 0) + edge["size"]
            colors[name] = edge["node"]["color"] or FG

    ranked = sorted(totals.items(), key=lambda kv: kv[1], reverse=True)[:6]
    grand_total = sum(v for _, v in ranked) or 1

    w = 480
    h = 40 + 26 * len(ranked) + 10
    body = [f'<text x="20" y="30" font-size="13" fill="{DIM}">top languages, by bytes</text>']
    y = 55
    bar_max = 260
    for name, size in ranked:
        pct = size / grand_total
        bar_w = max(4, int(pct * bar_max))
        color = colors.get(name, FG)
        body.append(f'<rect x="140" y="{y - 12}" width="{bar_w}" height="12" fill="{color}" rx="2"/>')
        body.append(f'<text x="20" y="{y - 2}" font-size="12" fill="{FG}">{esc(name)}</text>')
        body.append(f'<text x="{140 + bar_max + 10}" y="{y - 2}" font-size="11" fill="{DIM}">{pct*100:.1f}%</text>')
        y += 26

    with open(out_path, "w") as f:
        f.write(svg_wrap(w, h, "\n".join(body)))


def gen_year(days, out_path):
    # one char per day, column-major weeks, using the portrait ramp
    max_c = max((c for _, c in days), default=1) or 1
    n = len(RAMP) - 1

    weeks = [days[i:i + 7] for i in range(0, len(days), 7)]
    cell = 11
    w = 20 + len(weeks) * cell
    h = 20 + 7 * cell

    body = []
    for wi, week in enumerate(weeks):
        for di, (date, count) in enumerate(week):
            idx = int(round((count / max_c) * n)) if max_c else 0
            char = RAMP[idx]
            x = 15 + wi * cell
            y = 15 + di * cell
            body.append(f'<text x="{x}" y="{y}" font-size="10" fill="{FG}">{esc(char)}</text>')

    with open(out_path, "w") as f:
        f.write(svg_wrap(w, h, "\n".join(body)))


def main():
    user = fetch()
    collection = user["contributionsCollection"]
    total = collection["contributionCalendar"]["totalContributions"]
    days = flatten_days(collection)

    weeks = collection["contributionCalendar"]["weeks"]
    weekly_counts = [sum(d["contributionCount"] for d in wk["contributionDays"]) for wk in weeks]

    streaks = compute_streaks(days)
    repos = user["repositories"]["nodes"]

    gen_hero_stats(total, weekly_counts, "stats.svg")
    gen_streak(streaks, "streak.svg")
    gen_langs(repos, "langs.svg")
    gen_year(days, "year.svg")

    print(f"total={total} current_streak={streaks['current']} longest_streak={streaks['longest']}")


if __name__ == "__main__":
    main()
