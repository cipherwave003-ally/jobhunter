"""
RemoteOK Scraper — public API, no login needed.
"""

import time
import requests
from datetime import datetime
from bs4 import BeautifulSoup

TAGS = ["cybersecurity", "security-engineer", "infosec", "devsecops", "soc-analyst"]

HEADERS = {"User-Agent": "JobHunter/1.0 (personal job search automation)"}

# Title must contain one of these exact phrases
TITLE_MUST_HAVE = [
    "security engineer", "security analyst", "cyber", "infosec",
    "soc analyst", "penetration", "vulnerability", "forensic",
    "threat intelligence", "incident response", "devsecops",
    "security architect", "security operations", "appsec",
    "application security", "cloud security", "siem", "soar",
    "security researcher", "red team", "blue team", "security lead",
    "security manager", "security consultant", "it security",
]

# Title must NOT contain these (noise filter)
TITLE_EXCLUDE = [
    "officer", "associate", "chief of staff", "community",
    "director", "vp ", "head of", "recruiter", "sales",
    "marketing", "designer", "courier", "driver",
]


def _is_relevant(title: str) -> bool:
    t = title.lower()
    if any(ex in t for ex in TITLE_EXCLUDE):
        return False
    return any(k in t for k in TITLE_MUST_HAVE)


def scrape(max_results: int = 20) -> list:
    jobs = []
    seen = set()

    for tag in TAGS:
        try:
            resp = requests.get(
                f"https://remoteok.com/api?tag={tag}",
                headers=HEADERS,
                timeout=10,
            )
            if resp.status_code != 200:
                print(f"  ⚠ RemoteOK: status {resp.status_code} for tag={tag}")
                continue

            data = resp.json()
            for item in data[1:]:
                if not isinstance(item, dict):
                    continue

                title   = item.get("position", "")
                company = item.get("company", "")
                url     = item.get("url", "")
                ext_id  = "ro_" + str(item.get("id", url[-8:]))

                if not title or not company:
                    continue
                if ext_id in seen:
                    continue
                if not _is_relevant(title):
                    continue

                seen.add(ext_id)
                jobs.append({
                    "external_id": ext_id,
                    "platform":    "remoteok",
                    "title":       title,
                    "company":     company,
                    "location":    "Remote",
                    "salary":      item.get("salary", ""),
                    "url":         url,
                    "description": BeautifulSoup(
                        item.get("description", ""), "html.parser"
                    ).get_text()[:4000],
                    "job_type":    "remote",
                    "scraped_at":  datetime.utcnow().isoformat(),
                })

                if len(jobs) >= max_results:
                    break

            time.sleep(1)

        except Exception as e:
            print(f"  ⚠ RemoteOK error for tag={tag}: {e}")
            continue

    print(f"  ✓ RemoteOK: {len(jobs)} relevant jobs scraped")
    return jobs
