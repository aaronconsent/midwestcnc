#!/usr/bin/env python3
"""
Insights publishing schedule manager.

Assigns aspirational target publish dates to planned cluster articles
in src/data/insights-pillars.json. Articles still go through the full
6-step prompt chain + 11 quality gates + the 60-second human review
on the actual publish day — the schedule is a roadmap, not a
publish-on-date scheduler.

Schedule slips are normal and expected. The proprietary-signal gate
is the load-bearing constraint, not the calendar.

Usage:
  python3 scripts/insights_schedule.py auto-assign [--cadence 2] [--start YYYY-MM-DD] [--strategy round-robin|sequential] [--dry-run]
  python3 scripts/insights_schedule.py list [--days N] [--pillar SLUG]
  python3 scripts/insights_schedule.py clear
  python3 scripts/insights_schedule.py report
  python3 scripts/insights_schedule.py status
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import List, Tuple

REPO = Path(__file__).resolve().parent.parent
DATA = REPO / "src" / "data" / "insights-pillars.json"
DOC_OUT = REPO / "docs" / "insights-schedule.md"
PUBLISHED_DIR = REPO / "src" / "content" / "insights"


# ---------- Data IO ----------

def load_data() -> dict:
    return json.loads(DATA.read_text(encoding="utf-8"))


def save_data(data: dict) -> None:
    DATA.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def is_published(pillar_slug: str, cluster_slug: str) -> bool:
    return (PUBLISHED_DIR / pillar_slug / f"{cluster_slug}.md").exists()


# ---------- Date helpers ----------

def next_weekday_on_or_after(date: _dt.date, weekday: int) -> _dt.date:
    """Return the first date on or after `date` whose weekday matches."""
    days_ahead = (weekday - date.weekday()) % 7
    return date + _dt.timedelta(days=days_ahead)


def next_monday(today: _dt.date) -> _dt.date:
    """Return next Monday (strictly in the future if today is Monday)."""
    days_ahead = (7 - today.weekday()) % 7
    if days_ahead == 0:
        days_ahead = 7
    return today + _dt.timedelta(days=days_ahead)


# Cadence → which weekdays within a week articles ship on.
# Tuesday and Thursday are the sweet spot for B2B technical content
# (mid-week, away from Monday inbox triage and Friday wind-down).
WEEKLY_PUB_DAYS = {
    1: [1],            # Tue
    2: [1, 3],         # Tue, Thu
    3: [1, 2, 3],      # Tue, Wed, Thu
    4: [1, 2, 3, 4],   # Tue, Wed, Thu, Fri
}


# ---------- Auto-assign ----------

def _build_queue(data: dict, strategy: str) -> List[Tuple[str, dict]]:
    """Return (pillar_slug, cluster) tuples for every unpublished AND
    unscheduled cluster, in the order they should be drafted."""
    pillars = data["pillars"]
    queue: List[Tuple[str, dict]] = []

    if strategy == "round-robin":
        # Interleave: pillar1[0], pillar2[0], ... pillarN[0], pillar1[1], ...
        # This builds topical breadth across the site faster, which
        # compounds ranking signal more efficiently than going deep on
        # one pillar before starting the next.
        max_len = max((len(p["clusters"]) for p in pillars), default=0)
        for i in range(max_len):
            for p in pillars:
                if i >= len(p["clusters"]):
                    continue
                c = p["clusters"][i]
                if is_published(p["slug"], c["slug"]):
                    continue
                if c.get("target_publish_date"):
                    continue
                queue.append((p["slug"], c))
    else:
        # Sequential: all of pillar 1, then all of pillar 2, ...
        for p in pillars:
            for c in p["clusters"]:
                if is_published(p["slug"], c["slug"]):
                    continue
                if c.get("target_publish_date"):
                    continue
                queue.append((p["slug"], c))
    return queue


def auto_assign(data: dict, *, cadence: int, start_date: _dt.date,
                strategy: str) -> int:
    """Walk forward in weekly chunks, assigning target_publish_date to
    every cluster in the queue. Returns count assigned."""
    queue = _build_queue(data, strategy)
    if not queue:
        return 0
    pub_days = WEEKLY_PUB_DAYS.get(cadence, [1, 3])

    # start_date is assumed to be a Monday; we offset within the week
    # by the publish-day weekday index.
    week_start = start_date - _dt.timedelta(days=start_date.weekday())
    q_idx = 0
    while q_idx < len(queue):
        for wd in pub_days:
            if q_idx >= len(queue):
                break
            target = week_start + _dt.timedelta(days=wd)
            _, cluster = queue[q_idx]
            cluster["target_publish_date"] = target.isoformat()
            q_idx += 1
        week_start += _dt.timedelta(days=7)
    return q_idx


def unschedule_all(data: dict) -> int:
    """Clear target_publish_date from every cluster. Returns count cleared."""
    n = 0
    for p in data["pillars"]:
        for c in p["clusters"]:
            if c.pop("target_publish_date", None):
                n += 1
    return n


# ---------- Report writers ----------

def write_report(data: dict) -> None:
    pillars = data["pillars"]
    dated = []
    for p in pillars:
        for c in p["clusters"]:
            d = c.get("target_publish_date")
            if d:
                dated.append((d, p["slug"], p["title"], c))
    dated.sort(key=lambda t: t[0])

    lines: List[str] = [
        "# Insights Publishing Schedule\n",
        ("> **Internal roadmap.** Aspirational target dates for the planned "
         "cluster articles in [`src/data/insights-pillars.json`](../src/data/insights-pillars.json). "
         "Articles still pass through the full 6-step prompt chain + 11 quality "
         "gates + 60-second human review on the actual publish day. Schedule "
         "slips are expected when Ken's proprietary signal isn't ready for a "
         "given week — that's working as intended.\n"),
    ]

    # Headline numbers
    today = _dt.date.today()
    n_scheduled = len(dated)
    n_published = sum(
        1 for p in pillars for c in p["clusters"]
        if is_published(p["slug"], c["slug"])
    )
    n_total = sum(len(p["clusters"]) for p in pillars)
    n_unscheduled = n_total - n_scheduled - n_published

    lines.append("## Status\n")
    lines.append(f"- **Published:** {n_published}")
    lines.append(f"- **Scheduled (not yet drafted):** {n_scheduled}")
    lines.append(f"- **Unscheduled backlog:** {n_unscheduled}")
    lines.append(f"- **Total planned across all pillars:** {n_total}\n")

    if dated:
        first, last = dated[0][0], dated[-1][0]
        lines.append(f"First scheduled date: `{first}`. Last: `{last}`.\n")

    # Calendar view (by week, ascending)
    lines.append("## Calendar\n")
    if not dated:
        lines.append("_No articles scheduled yet. Run `python3 scripts/insights_schedule.py auto-assign` to populate._\n")
    else:
        by_week = defaultdict(list)
        for d_str, ps, pt, c in dated:
            dt = _dt.date.fromisoformat(d_str)
            monday = dt - _dt.timedelta(days=dt.weekday())
            by_week[monday].append((dt, ps, pt, c))
        for monday in sorted(by_week.keys()):
            week_label = monday.strftime("%b %-d, %Y")
            is_past = monday < today - _dt.timedelta(days=7)
            marker = " &mdash; *past*" if is_past else ""
            lines.append(f"### Week of {week_label}{marker}\n")
            for dt, ps, pt, c in by_week[monday]:
                day_label = dt.strftime("%a %b %-d")
                pub_marker = " ✓" if is_published(ps, c["slug"]) else ""
                lines.append(
                    f"- **{day_label}** &mdash; *{pt}* &mdash; "
                    f"[{c['title']}](../src/content/insights/{ps}/{c['slug']}.md){pub_marker}"
                )
            lines.append("")

    # Per-pillar view
    lines.append("## By Pillar\n")
    for p in pillars:
        pub_count = sum(1 for c in p["clusters"] if is_published(p["slug"], c["slug"]))
        sched_count = sum(
            1 for c in p["clusters"]
            if c.get("target_publish_date") and not is_published(p["slug"], c["slug"])
        )
        unsched_count = len(p["clusters"]) - pub_count - sched_count
        lines.append(f"### {p['title']}\n")
        lines.append(
            f"_{pub_count} published &middot; {sched_count} scheduled &middot; "
            f"{unsched_count} unscheduled (of {len(p['clusters'])} total)._\n"
        )

        # Sort: published first, then by date ascending, then unscheduled
        rows = []
        for c in p["clusters"]:
            if is_published(p["slug"], c["slug"]):
                rows.append(("0_published", c.get("target_publish_date", "—"), c))
            elif c.get("target_publish_date"):
                rows.append(("1_scheduled", c["target_publish_date"], c))
            else:
                rows.append(("2_unscheduled", "—", c))
        rows.sort(key=lambda r: (r[0], r[1]))
        for status, date, c in rows:
            if status == "0_published":
                lines.append(f"- ✓ **{date}** &mdash; ~~{c['title']}~~ (published)")
            elif status == "1_scheduled":
                lines.append(f"- ◯ `{date}` &mdash; {c['title']}")
            else:
                lines.append(f"- · *unscheduled* &mdash; {c['title']}")
        lines.append("")

    lines.append("---\n")
    lines.append("## Regenerating this report\n")
    lines.append("```bash\n")
    lines.append("python3 scripts/insights_schedule.py report\n")
    lines.append("```\n")
    lines.append("\n## Changing the schedule\n")
    lines.append("```bash\n")
    lines.append("# Clear everything and start fresh:\n")
    lines.append("python3 scripts/insights_schedule.py clear\n\n")
    lines.append("# Re-assign at 3/week starting July 1:\n")
    lines.append("python3 scripts/insights_schedule.py auto-assign --cadence 3 --start 2026-07-01\n\n")
    lines.append("# Pillar-sequential instead of round-robin:\n")
    lines.append("python3 scripts/insights_schedule.py auto-assign --strategy sequential\n")
    lines.append("```\n")

    DOC_OUT.parent.mkdir(parents=True, exist_ok=True)
    DOC_OUT.write_text("\n".join(lines), encoding="utf-8")


def print_list(data: dict, *, days: int | None, pillar: str | None) -> None:
    today = _dt.date.today()
    cutoff = today + _dt.timedelta(days=days) if days else None

    print(f"\n=== Insights publishing schedule (today: {today.isoformat()}) ===")
    if cutoff:
        print(f"Filter: next {days} days (through {cutoff.isoformat()})")
    if pillar:
        print(f"Filter: pillar = {pillar}")
    print()

    rows = []
    for p in data["pillars"]:
        if pillar and p["slug"] != pillar:
            continue
        for c in p["clusters"]:
            d = c.get("target_publish_date")
            if not d:
                continue
            dt = _dt.date.fromisoformat(d)
            if cutoff and dt > cutoff:
                continue
            rows.append((d, p["slug"], c))
    rows.sort(key=lambda r: r[0])

    if not rows:
        print("  (no scheduled articles match the filter)")
    else:
        for d, ps, c in rows:
            status = "✓ pub " if is_published(ps, c["slug"]) else "  plan"
            print(f"  {d}  [{status}]  {ps:<28}  {c['title']}")
    print()


def print_status(data: dict) -> None:
    pillars = data["pillars"]
    today = _dt.date.today()

    n_total = sum(len(p["clusters"]) for p in pillars)
    n_published = sum(
        1 for p in pillars for c in p["clusters"]
        if is_published(p["slug"], c["slug"])
    )
    n_scheduled = sum(
        1 for p in pillars for c in p["clusters"]
        if c.get("target_publish_date") and not is_published(p["slug"], c["slug"])
    )
    n_unscheduled = n_total - n_scheduled - n_published

    # Next 14 days
    horizon = today + _dt.timedelta(days=14)
    upcoming = []
    for p in pillars:
        for c in p["clusters"]:
            d = c.get("target_publish_date")
            if not d:
                continue
            if is_published(p["slug"], c["slug"]):
                continue
            dt = _dt.date.fromisoformat(d)
            if today <= dt <= horizon:
                upcoming.append((d, p["slug"], c))
    upcoming.sort(key=lambda r: r[0])

    overdue = []
    for p in pillars:
        for c in p["clusters"]:
            d = c.get("target_publish_date")
            if not d:
                continue
            if is_published(p["slug"], c["slug"]):
                continue
            dt = _dt.date.fromisoformat(d)
            if dt < today:
                overdue.append((d, p["slug"], c))
    overdue.sort(key=lambda r: r[0])

    print(f"\n=== Insights schedule status — {today.isoformat()} ===\n")
    print(f"  Published:                {n_published}")
    print(f"  Scheduled (not drafted):  {n_scheduled}")
    print(f"  Unscheduled backlog:      {n_unscheduled}")
    print(f"  Total planned:            {n_total}\n")

    if overdue:
        print(f"  ⚠  {len(overdue)} overdue article(s):")
        for d, ps, c in overdue[:5]:
            print(f"    {d}  {ps}  {c['title']}")
        if len(overdue) > 5:
            print(f"    ... and {len(overdue) - 5} more.")
        print()

    if upcoming:
        print(f"  → Next 14 days ({len(upcoming)} article(s)):")
        for d, ps, c in upcoming:
            print(f"    {d}  {ps}  {c['title']}")
    else:
        print("  → Nothing scheduled in the next 14 days.")
    print()


# ---------- CLI ----------

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_auto = sub.add_parser("auto-assign",
                            help="Assign target dates to every unpublished, unscheduled cluster")
    p_auto.add_argument("--cadence", type=int, default=2,
                        choices=[1, 2, 3, 4], help="Articles per week (default: 2)")
    p_auto.add_argument("--start", help="Start week (Monday) as YYYY-MM-DD (default: next Monday)")
    p_auto.add_argument("--strategy", choices=["round-robin", "sequential"],
                        default="round-robin",
                        help="round-robin interleaves pillars (default); sequential finishes one pillar before starting the next")
    p_auto.add_argument("--dry-run", action="store_true",
                        help="Show what would be assigned without saving")

    p_list = sub.add_parser("list", help="Print the schedule to stdout")
    p_list.add_argument("--days", type=int, help="Only show articles in next N days")
    p_list.add_argument("--pillar", help="Filter to a specific pillar slug")

    sub.add_parser("clear", help="Remove all target_publish_date values")
    sub.add_parser("report", help="Regenerate docs/insights-schedule.md")
    sub.add_parser("status", help="Quick summary + next 14 days + overdue")

    args = ap.parse_args()
    data = load_data()

    if args.cmd == "auto-assign":
        today = _dt.date.today()
        if args.start:
            start = _dt.date.fromisoformat(args.start)
        else:
            start = next_monday(today)
        # Ensure start is a Monday
        if start.weekday() != 0:
            start = start - _dt.timedelta(days=start.weekday())
            print(f"Note: snapping start date to Monday {start.isoformat()}.")

        # In dry-run mode we operate on a fresh copy
        target_data = json.loads(json.dumps(data)) if args.dry_run else data
        n = auto_assign(target_data, cadence=args.cadence,
                        start_date=start, strategy=args.strategy)

        if n == 0:
            print("\nNothing to schedule — every cluster is already published or already has a target date.")
            print("Run `clear` first if you want to re-assign from scratch.")
            return 0

        print(f"\nAssigned target dates to {n} cluster(s).")
        print(f"  Cadence:  {args.cadence}/week (Tue/Thu pattern)")
        print(f"  Strategy: {args.strategy}")
        print(f"  Start:    Monday {start.isoformat()}")
        # Compute end date
        n_weeks = (n + args.cadence - 1) // args.cadence
        end = start + _dt.timedelta(days=7 * n_weeks)
        print(f"  Runs through approximately {end.isoformat()} ({n_weeks} weeks)\n")

        if args.dry_run:
            print("(dry run — JSON not saved)")
        else:
            save_data(data)
            write_report(data)
            print(f"Wrote {DATA.relative_to(REPO)}")
            print(f"Wrote {DOC_OUT.relative_to(REPO)}")

    elif args.cmd == "list":
        print_list(data, days=args.days, pillar=args.pillar)

    elif args.cmd == "clear":
        n = unschedule_all(data)
        save_data(data)
        write_report(data)
        print(f"Cleared {n} target_publish_date value(s).")
        print(f"Wrote {DATA.relative_to(REPO)}")
        print(f"Wrote {DOC_OUT.relative_to(REPO)}")

    elif args.cmd == "report":
        write_report(data)
        print(f"Wrote {DOC_OUT.relative_to(REPO)}")

    elif args.cmd == "status":
        print_status(data)

    return 0


if __name__ == "__main__":
    sys.exit(main())
