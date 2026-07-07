"""
Tracker — saves application decisions and history to data/tracker.json
"""

import json
from datetime import datetime
from pathlib import Path

TRACKER_PATH = Path(__file__).parent.parent / "data" / "tracker.json"


def _load() -> list:
    if TRACKER_PATH.exists():
        return json.loads(TRACKER_PATH.read_text())
    return []


def _save(data: list):
    TRACKER_PATH.write_text(json.dumps(data, indent=2))


def save_decisions(results: list):
    """Save approve/skip decisions from popup to tracker."""
    history = _load()
    for r in results:
        job = r["job"]
        history.append({
            "date":          datetime.now().strftime("%Y-%m-%d %H:%M"),
            "action":        r["action"],
            "title":         job.get("title", ""),
            "company":       job.get("company", "") or "",
            "location":      job.get("location", ""),
            "platform":      job.get("platform", ""),
            "url":           job.get("url", ""),
            "match_score":   job.get("match_score", 0),
            "cover_letter":  r.get("cover_letter", ""),
            "status":        "applied" if r["action"] == "approve" else "skipped",
        })
    _save(history)
    print(f"  ✓ {len(results)} decisions saved to tracker")


def update_status(url: str, status: str):
    """Update status of an application — e.g. replied, interview, offer."""
    history = _load()
    for entry in history:
        if entry.get("url") == url:
            entry["status"] = status
            entry["updated"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    _save(history)


def get_stats() -> dict:
    history  = _load()
    applied  = [h for h in history if h["action"] == "approve"]
    skipped  = [h for h in history if h["action"] == "skip"]
    replied  = [h for h in history if h.get("status") == "replied"]
    interview= [h for h in history if h.get("status") == "interview"]
    offers   = [h for h in history if h.get("status") == "offer"]

    by_platform = {}
    for h in applied:
        p = h.get("platform", "unknown")
        by_platform[p] = by_platform.get(p, 0) + 1

    return {
        "total_applied":  len(applied),
        "total_skipped":  len(skipped),
        "replied":        len(replied),
        "interviews":     len(interview),
        "offers":         len(offers),
        "by_platform":    by_platform,
        "success_rate":   round(len(interview) / len(applied) * 100, 1) if applied else 0,
        "recent":         sorted(applied, key=lambda x: x["date"], reverse=True)[:10],
    }
