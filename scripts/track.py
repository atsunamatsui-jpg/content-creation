#!/usr/bin/env python3
"""
Campaign application tracker.

The follow-up is where most of the money is, and it is the part that depends on
memory. This makes it depend on a command instead.

    python3 scripts/track.py add --platform Aspire --brand Muji \
        --campaign "Spring kitchenware" --deliverables "1 TikTok + 2 Stories" \
        --rate 80000 --currency JPY
    python3 scripts/track.py due
    python3 scripts/track.py list [--status applied]
    python3 scripts/track.py status --brand Muji --set won --outcome "80000 JPY"
    python3 scripts/track.py stats
"""
import argparse
import csv
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CSV_PATH = REPO / "tracker" / "campaigns.csv"

FIELDS = ["date_applied", "platform", "brand", "campaign", "deliverables",
          "rate_quoted", "currency", "status", "followup_1_due", "followup_2_due",
          "outcome", "notes"]

# Follow-up #1 lands in the window where replies actually happen; #2 closes the loop.
FOLLOWUP_1_DAYS = 6
FOLLOWUP_2_DAYS = 21

OPEN_STATUSES = {"applied", "in_talks", "negotiating"}
CLOSED_STATUSES = {"won", "lost", "ghosted"}


def load():
    if not CSV_PATH.exists():
        return []
    with open(CSV_PATH, newline="", encoding="utf-8") as fh:
        return [r for r in csv.DictReader(fh) if any(v.strip() for v in r.values())]


def save(rows):
    CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CSV_PATH, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in FIELDS})


def parse_date(text):
    try:
        return datetime.strptime(text.strip(), "%Y-%m-%d").date()
    except (ValueError, AttributeError):
        return None


def cmd_add(args):
    applied = parse_date(args.date) if args.date else date.today()
    if applied is None:
        sys.exit(f"Bad --date (expected YYYY-MM-DD): {args.date}")
    rows = load()
    rows.append({
        "date_applied": applied.isoformat(),
        "platform": args.platform,
        "brand": args.brand,
        "campaign": args.campaign or "",
        "deliverables": args.deliverables or "",
        "rate_quoted": str(args.rate or ""),
        "currency": args.currency or "",
        "status": "applied",
        "followup_1_due": (applied + timedelta(days=FOLLOWUP_1_DAYS)).isoformat(),
        "followup_2_due": (applied + timedelta(days=FOLLOWUP_2_DAYS)).isoformat(),
        "outcome": "",
        "notes": args.notes or "",
    })
    save(rows)
    print(f"Logged {args.brand} via {args.platform}.")
    print(f"  Follow up #1: {rows[-1]['followup_1_due']}")
    print(f"  Follow up #2: {rows[-1]['followup_2_due']}")


def cmd_due(args):
    today = date.today()
    rows = load()
    pending = []
    for row in rows:
        if row.get("status", "") not in OPEN_STATUSES:
            continue
        # Surface the latest follow-up that has come due. If #2's date has
        # passed too, #1's window is long gone — send the close-the-loop one.
        for n, col in ((2, "followup_2_due"), (1, "followup_1_due")):
            due = parse_date(row.get(col, ""))
            if due and due <= today:
                pending.append((due, n, row))
                break
    if not pending:
        open_count = sum(1 for r in rows if r.get("status") in OPEN_STATUSES)
        print(f"Nothing due. {open_count} application(s) still open.")
        return
    pending.sort(key=lambda p: p[0])
    print(f"{len(pending)} follow-up(s) due:\n")
    for due, n, row in pending:
        overdue = (today - due).days
        late = f"  ({overdue}d overdue)" if overdue > 0 else "  (due today)"
        print(f"  [#{n}] {row['brand']} — {row['campaign'] or 'campaign'} "
              f"via {row['platform']}{late}")
        which = "message #1" if n == 1 else "message #2 (close the loop)"
        print(f"        applied {row['date_applied']}  ·  "
              f"templates/follow-up.md — {which}")
    print("\nSend them, then update: python3 scripts/track.py status --brand X --set in_talks")


def cmd_list(args):
    rows = load()
    if args.status:
        rows = [r for r in rows if r.get("status") == args.status]
    if not rows:
        print("No matching applications.")
        return
    width = max(len(r["brand"]) for r in rows) + 2
    for row in sorted(rows, key=lambda r: r.get("date_applied", "")):
        print(f"{row['date_applied']}  {row['brand']:<{width}}"
              f"{row['platform']:<18}{row['status']:<13}{row.get('outcome','')}")


def cmd_status(args):
    rows = load()
    matches = [r for r in rows if r["brand"].lower() == args.brand.lower()]
    if args.campaign:
        matches = [r for r in matches if r["campaign"].lower() == args.campaign.lower()]
    if not matches:
        sys.exit(f"No application logged for brand: {args.brand}")
    if len(matches) > 1:
        sys.exit(f"{len(matches)} applications match '{args.brand}'. "
                 f"Narrow it with --campaign.")
    valid = OPEN_STATUSES | CLOSED_STATUSES
    if args.set not in valid:
        sys.exit(f"Status must be one of: {', '.join(sorted(valid))}")
    matches[0]["status"] = args.set
    if args.outcome:
        matches[0]["outcome"] = args.outcome
    if args.notes:
        matches[0]["notes"] = args.notes
    save(rows)
    print(f"{matches[0]['brand']} -> {args.set}")


def cmd_stats(args):
    rows = load()
    if not rows:
        print("Nothing logged yet.")
        return
    total = len(rows)
    won = [r for r in rows if r.get("status") == "won"]
    closed = [r for r in rows if r.get("status") in CLOSED_STATUSES]
    print(f"Applications:  {total}")
    print(f"Still open:    {sum(1 for r in rows if r.get('status') in OPEN_STATUSES)}")
    print(f"Won:           {len(won)}")
    if closed:
        print(f"Win rate:      {len(won) / len(closed):.0%}  (of {len(closed)} closed)")

    by_platform = {}
    for row in rows:
        p = by_platform.setdefault(row["platform"], {"n": 0, "won": 0})
        p["n"] += 1
        if row.get("status") == "won":
            p["won"] += 1
    print("\nBy platform:")
    for name, s in sorted(by_platform.items(), key=lambda kv: -kv[1]["won"]):
        rate = f"{s['won'] / s['n']:.0%}" if s["n"] else "—"
        print(f"  {name:<22}{s['won']}/{s['n']}  ({rate})")
    print("\nDrop platforms that stay at 0 after ~15 applications and put "
          "that time into the ones converting.")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("add", help="Log a new application")
    a.add_argument("--platform", required=True)
    a.add_argument("--brand", required=True)
    a.add_argument("--campaign")
    a.add_argument("--deliverables")
    a.add_argument("--rate")
    a.add_argument("--currency")
    a.add_argument("--date", help="YYYY-MM-DD (default: today)")
    a.add_argument("--notes")
    a.set_defaults(func=cmd_add)

    d = sub.add_parser("due", help="Follow-ups due now")
    d.set_defaults(func=cmd_due)

    l = sub.add_parser("list", help="List applications")
    l.add_argument("--status")
    l.set_defaults(func=cmd_list)

    s = sub.add_parser("status", help="Update an application's status")
    s.add_argument("--brand", required=True)
    s.add_argument("--campaign")
    s.add_argument("--set", required=True)
    s.add_argument("--outcome")
    s.add_argument("--notes")
    s.set_defaults(func=cmd_status)

    st = sub.add_parser("stats", help="Win rate by platform")
    st.set_defaults(func=cmd_stats)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
