"""
Greenhouse ATS Scraper
Pulls jobs directly from companies' Greenhouse boards via public API.
No auth needed — Greenhouse exposes all job listings publicly.
Auto-apply supported via automation/greenhouse_apply.py
"""

import re
import time
import hashlib
import requests
from datetime import datetime
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "JobHunter/1.0 (personal job search automation)"}

# Cybersecurity companies using Greenhouse — add more as you find them
# Slug is the company identifier in boards.greenhouse.io/<slug>/jobs
COMPANIES = [
    # Cybersecurity companies
    ("okta",              "Okta"),
    ("zscaler",           "Zscaler"),
    ("onetrust",          "OneTrust"),
    ("logicgate",         "LogicGate"),
    ("obsidiansecurity",  "Obsidian Security"),
    ("lacework",          "Lacework"),
    ("snyk",              "Snyk"),
    ("hackerone",         "HackerOne"),
    ("bugcrowd",          "Bugcrowd"),
    ("tenable",           "Tenable"),
    ("rapid7",            "Rapid7"),
    ("secureworks",       "Secureworks"),
    ("arcsight",          "ArcSight"),
    # Tech companies with large security teams
    ("cloudflare",        "Cloudflare"),
    ("hashicorp",         "HashiCorp"),
    ("mongodb",           "MongoDB"),
    ("gitlab",            "GitLab"),
    ("automatticcareers", "Automattic"),
]

TITLE_MUST = [
    "security", "cyber", "soc", "penetration", "vulnerability",
    "forensic", "threat", "incident", "devsecops", "infosec",
    "appsec", "detection", "cloud security", "grc", "compliance",
    "identity", "iam", "zero trust", "siem", "soar"
]

TITLE_EXCLUDE = [
    "intern", "fresher", "director", "vp ", "vice president",
    "head of", "chief", "junior", "sales", "marketing",
    "recruiter", "counsel", "lawyer", "finance", "accounting"
]


def _job_id(company_slug: str, job_id: str) -> str:
    return f"gh_{company_slug}_{job_id}"


def _is_relevant(title: str) -> bool:
    t = title.lower()
    if any(x in t for x in TITLE_EXCLUDE):
        return False
    return any(re.search(r"\b" + re.escape(k) + r"\b", t) for k in TITLE_MUST)


def _fetch_description(job_id: str, company_slug: str) -> str:
    try:
        url  = f"https://boards-api.greenhouse.io/v1/boards/{company_slug}/jobs/{job_id}"
        resp = requests.get(url, headers=HEADERS, timeout=10)
        if resp.status_code == 200:
            data    = resp.json()
            content = data.get("content", "")
            return BeautifulSoup(content, "html.parser").get_text(separator="\n").strip()[:4000]
    except Exception:
        pass
    return ""


def scrape_company(slug: str, company_name: str) -> list:
    jobs = []
    try:
        url  = f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs"
        resp = requests.get(url, headers=HEADERS, timeout=10)
        if resp.status_code != 200:
            return []

        data     = resp.json()
        all_jobs = data.get("jobs", [])
        relevant = [j for j in all_jobs if _is_relevant(j.get("title", ""))]
        print(f"    {company_name}: {len(all_jobs)} total, {len(relevant)} security roles")

        for j in relevant:
            job_id   = str(j.get("id", ""))
            title    = j.get("title", "")
            location = j.get("location", {}).get("name", "")
            url      = j.get("absolute_url", f"https://boards.greenhouse.io/{slug}/jobs/{job_id}")

            jobs.append({
                "external_id": _job_id(slug, job_id),
                "platform":    "greenhouse",
                "title":       title,
                "company":     company_name,
                "location":    location,
                "salary":      "",
                "url":         url,
                "description": _fetch_description(job_id, slug),
                "job_type":    "full-time",
                "scraped_at":  datetime.utcnow().isoformat(),
                "ats":         "greenhouse",
                "ats_job_id":  job_id,
                "ats_slug":    slug,
            })
            time.sleep(0.3)

    except Exception as e:
        print(f"    {company_name}: error — {e}")

    return jobs


def scrape(max_results: int = 30) -> list:
    all_jobs = []
    seen     = set()

    print(f"  Scanning {len(COMPANIES)} companies on Greenhouse...")
    for slug, name in COMPANIES:
        if len(all_jobs) >= max_results:
            break
        company_jobs = scrape_company(slug, name)
        for j in company_jobs:
            if j["external_id"] not in seen:
                seen.add(j["external_id"])
                all_jobs.append(j)
        time.sleep(0.5)

    print(f"  ✓ Greenhouse: {len(all_jobs)} security jobs scraped")
    return all_jobs
