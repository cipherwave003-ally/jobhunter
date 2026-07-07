import sys, os, argparse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime

def run_pipeline():
    print(f"\n{'='*50}")
    print(f"JobHunter Daily Run — {datetime.now().strftime('%d %b %Y %H:%M')}")
    print(f"{'='*50}\n")

    from scrapers.runner import run_all
    from core.matcher import batch_score, filter_by_score
    from core.cover_letter import batch_generate
    from ui.popup import show_approval_popup
    from core.tracker import save_decisions

    jobs     = run_all(max_per_source=15)
    scored   = batch_score(jobs)
    filtered = filter_by_score(scored, min_score=45)

    if not filtered:
        print("No matching jobs found today.")
        return

    filtered = batch_generate(filtered)
    print(f"\nOpening popup with {len(filtered)} matches...\n")
    results  = show_approval_popup(filtered)
    save_decisions(results)

    approved = [r for r in results if r["action"] == "approve"]
    skipped  = [r for r in results if r["action"] == "skip"]
    print(f"\n✓ Done — Approved: {len(approved)} | Skipped: {len(skipped)}")
    print("Run 'python3 dashboard.py' to see your stats.\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--now", action="store_true")
    args = parser.parse_args()

    if args.now:
        run_pipeline()
    else:
        from apscheduler.schedulers.blocking import BlockingScheduler
        from apscheduler.triggers.cron import CronTrigger
        scheduler = BlockingScheduler(timezone="Asia/Kolkata")
        scheduler.add_job(run_pipeline, CronTrigger(hour=9, minute=0, timezone="Asia/Kolkata"))
        print("Scheduler started — runs daily at 09:00 IST. Ctrl+C to stop.")
        try:
            scheduler.start()
        except KeyboardInterrupt:
            print("\nScheduler stopped.")
