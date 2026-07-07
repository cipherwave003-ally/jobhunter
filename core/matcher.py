"""
Offline matcher — scores jobs against your profile using keyword analysis.
No API needed. Swap AI_MODE = True later to use Claude API.
"""

import re
import json
from pathlib import Path

AI_MODE = False  # Set True once you add ANTHROPIC_API_KEY to .env

PROFILE_PATH = Path(__file__).parent.parent / "data" / "profile.json"


def _load_profile() -> dict:
    if PROFILE_PATH.exists():
        return json.loads(PROFILE_PATH.read_text())
    return {}


def score_job(job: dict) -> dict:
    if AI_MODE:
        return _score_ai(job)
    return _score_offline(job)


def _score_offline(job: dict) -> dict:
    profile  = _load_profile()
    skills   = [s.lower() for s in profile.get("skills", [])]
    certs    = [c.lower() for c in profile.get("certifications", [])]
    years    = profile.get("years_experience", 3)
    locations = [l.lower() for l in ["bengaluru", "bangalore", "remote",
                                      "work from home", "india", "hyderabad",
                                      "mumbai", "chennai", "pune"]]

    title       = job.get("title", "").lower()
    description = job.get("description", "").lower()
    location    = job.get("location", "").lower()
    full_text   = f"{title} {description}"

    score   = 0
    reasons = []
    flags   = []

    # ── Skill match (40 points) ───────────────────────────────────────────
    matched_skills = [s for s in skills if s in full_text]
    skill_score = min(40, int((len(matched_skills) / max(len(skills), 1)) * 60))
    score += skill_score
    if matched_skills:
        top = matched_skills[:4]
        reasons.append(f"Matches your skills: {', '.join(top)}")

    # ── Title relevance (20 points) ───────────────────────────────────────
    title_keywords = [
        "security", "cyber", "soc", "penetration", "vulnerability",
        "forensic", "threat", "incident", "devsecops", "infosec",
        "appsec", "detection", "cloud security", "siem", "soar"
    ]
    title_hits = [k for k in title_keywords if k in title]
    if title_hits:
        score += 20
        reasons.append(f"Title matches: {', '.join(title_hits[:2])}")
    else:
        flags.append("Title doesn't clearly match cybersecurity")

    # ── Experience level (20 points) ──────────────────────────────────────
    exp_patterns = [
        (r'\b([2-5])\+?\s*years?\b', 20, "Experience level matches"),
        (r'\bmid[\s-]level\b',       20, "Mid-level role"),
        (r'\bsenior\b',              10, "Senior role — slightly above target"),
        (r'\bjunior\b',               0, "Junior role — below target"),
        (r'\bfresher\b',              0, "Fresher role — not relevant"),
    ]
    exp_score = 0
    for pattern, pts, reason in exp_patterns:
        if re.search(pattern, full_text):
            exp_score = pts
            if pts > 0:
                reasons.append(reason)
            else:
                flags.append(reason)
            break
    else:
        exp_score = 10  # no explicit mention, neutral
    score += exp_score

    # ── Location match (10 points) ────────────────────────────────────────
    if any(loc in location for loc in locations):
        score += 10
        reasons.append(f"Location match: {job.get('location','')}")
    elif "remote" in full_text:
        score += 8
        reasons.append("Remote friendly")
    else:
        flags.append("Location unclear")

    # ── Certification bonus (10 points) ───────────────────────────────────
    matched_certs = [c for c in certs if c.split("(")[0].strip() in full_text]
    if matched_certs:
        score += 10
        reasons.append(f"Cert mentioned: {matched_certs[0]}")

    # ── Exclusion penalty ─────────────────────────────────────────────────
    exclude = ["intern", "fresher", "0-1 year", "director", "vp ", "10+ years"]
    for ex in exclude:
        if ex in full_text:
            score = max(0, score - 20)
            flags.append(f"Contains exclusion term: '{ex}'")
            break

    return {
        "score":     min(100, score),
        "reasons":   reasons,
        "red_flags": flags,
    }


def _score_ai(job: dict) -> dict:
    """AI scoring via Claude API — activated when AI_MODE = True."""
    try:
        import anthropic, os
        from pathlib import Path

        # Load API key from .env
        env = Path(__file__).parent.parent / ".env"
        if env.exists():
            for line in env.read_text().splitlines():
                if "ANTHROPIC_API_KEY" in line:
                    k, v = line.split("=", 1)
                    os.environ.setdefault("ANTHROPIC_API_KEY", v.strip().strip('"'))

        profile = _load_profile()
        client  = anthropic.Anthropic()

        prompt = f"""Score this cybersecurity job match from 0-100.

Candidate: {profile.get('years_experience')} years exp, skills: {', '.join(profile.get('skills', [])[:10])}

Job: {job.get('title')} at {job.get('company')}
Location: {job.get('location')}
Description: {job.get('description','')[:2000]}

Respond ONLY with JSON, no markdown:
{{"score": 75, "reasons": ["reason1", "reason2"], "red_flags": ["flag1"]}}"""

        resp = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=300,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = resp.content[0].text.strip()
        return json.loads(raw)
    except Exception as e:
        print(f"  ⚠ AI scoring failed, falling back to offline: {e}")
        return _score_offline(job)


def batch_score(jobs: list) -> list:
    """Score a list of jobs, return sorted by score descending."""
    print(f"  Scoring {len(jobs)} jobs...")
    for job in jobs:
        result = score_job(job)
        job["match_score"]   = result["score"]
        job["match_reasons"] = result["reasons"]
        job["red_flags"]     = result.get("red_flags", [])
    return sorted(jobs, key=lambda j: j["match_score"], reverse=True)


def filter_by_score(jobs: list, min_score: int = 50) -> list:
    return [j for j in jobs if j.get("match_score", 0) >= min_score]
