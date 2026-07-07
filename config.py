"""
JobHunter — Your profile and search preferences.
Edit this file or run: python3 setup.py
"""

from pathlib import Path

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

# ── Your profile ─────────────────────────────────────────────────────────────
PROFILE = {
    "name":             "",
    "email":            "",
    "phone":            "",
    "location":         "Bengaluru, Karnataka, India",
    "linkedin_url":     "",
    "github_url":       "",
    "portfolio_url":    "",
    "resume_path":      "",
    "years_experience": 3,
    "notice_period":    "Immediate",
    "expected_salary":  "",
    "current_title":    "Cybersecurity Engineer",
    "skills": [
        "Penetration Testing", "Vulnerability Assessment", "SIEM",
        "Incident Response", "SOC", "Network Security", "Python",
        "Burp Suite", "Metasploit", "Nessus", "Wireshark",
        "AWS Security", "ISO 27001", "OWASP",
    ],
    "certifications": [],
    "summary": "",
}

# ── Search preferences ────────────────────────────────────────────────────────
SEARCH_PREFS = {
    "keywords": [
        "cybersecurity analyst", "information security analyst",
        "SOC analyst", "penetration tester", "security engineer",
        "application security", "cloud security engineer",
        "vulnerability analyst", "threat intelligence analyst",
    ],
    "locations": [
        "Bengaluru", "Hyderabad", "Mumbai", "Chennai",
        "Remote", "Work from home",
    ],
    "exclude_keywords": [
        "fresher", "0-1 year", "intern", "10+ years", "director",
    ],
    "min_match_score":      55,
    "max_jobs_per_run":     50,
    "apply_limit_per_day":  15,
}
