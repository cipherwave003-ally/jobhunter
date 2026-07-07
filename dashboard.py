"""
JobHunter Dashboard
Shows application stats and history in the terminal.
Run: python3 dashboard.py
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.tracker import get_stats
from datetime import datetime


def show():
    stats = get_stats()

    print()
    print("=" * 52)
    print("  JobHunter Dashboard")
    print(f"  {datetime.now().strftime('%d %b %Y %H:%M')}")
    print("=" * 52)

    print(f"""
  Applied       {stats["total_applied"]:>4}
  Skipped       {stats["total_skipped"]:>4}
  Replied       {stats["replied"]:>4}
  Interviews    {stats["interviews"]:>4}
  Offers        {stats["offers"]:>4}
  Success rate  {stats["success_rate"]:>3}%
""")

    if stats["by_platform"]:
        print("  By platform:")
        for platform, count in sorted(stats["by_platform"].items(), key=lambda x: -x[1]):
            bar = "█" * count
            print(f"    {platform:<14} {bar} {count}")
        print()

    if stats["recent"]:
        print("  Recent applications:")
        print(f"  {'Date':<17} {'Score':<7} {'Title':<30} {'Company'}")
        print("  " + "-" * 70)
        for h in stats["recent"]:
            title   = h.get("title","")[:28]
            company = h.get("company","")[:20]
            score   = h.get("match_score", 0)
            date    = h.get("date","")[:16]
            status  = h.get("status","")
            status_icon = {"applied":"📤","replied":"💬","interview":"🎯","offer":"🎉","skipped":"⏭"}.get(status,"•")
            print(f"  {date:<17} {score:<7} {title:<30} {company} {status_icon}")
    else:
        print("  No applications yet — run python3 scheduler.py --now to start!")

    print()
    print("  To update a job status:")
    print("  python3 dashboard.py --update <url> <status>")
    print("  Status options: replied | interview | offer | rejected")
    print()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--update", nargs=2, metavar=("URL", "STATUS"),
                        help="Update status of an application")
    args = parser.parse_args()

    if args.update:
        from core.tracker import update_status
        url, status = args.update
        update_status(url, status)
        print(f"✓ Updated status to '{status}' for {url[:60]}")
    else:
        show()
