"""
Himalayas Scraper — official free public JSON API, no auth needed.
Docs: https://himalayas.app/api
"""

import re
import time
import requests
from datetime import datetime
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "JobHunter/1.0 (personal job search automation)"}
SEARCH_URL = "https://himalayas.app/jobs/api/search"

KEYWORDS = [
    "cybersecurity",
    "security engineer",
    "soc analyst",
    "incident response",
    "penetration testing",
    "detection engineering",
]

TITLE_EXCLUDE = [
    "intern", "fresher", "director", "vp ", "vice president",
    "head of", "chief", "junior", "sales", "marketing"
]


def _is_relevant(title: str) -> bool:
    t = title.lower()
    return not any(x in t for x in TITLE_EXCLUDE)


def _clean_html(html: str) -> str:
    return BeautifulSoup(html, "html.parser").get_text(separator="\n").strip()[:4000]


def scrape(max_results: int = 20) -> list:
    jobs = []
    seen = set()

    for keyword in KEYWORDS:
        if len(jobs) >= max_results:
            break

        params = {
            "q":        keyword,
            "sort":     "recent",
        }

        try:
            resp = requests.get(SEARCH_URL, params=params, headers=HEADERS, timeout=12)
            if resp.status_code != 200:
                print(f"  Himalayas: status {resp.status_code} for '{keyword}'")
                continue

            data    = resp.json()
            results = data if isinstance(data, list) else data.get("jobs", data.get("results", []))
            print(f"  {len(results)} results for '{keyword}'")

            for item in results:
                if len(jobs) >= max_results:
                    break

                title = item.get("title", "")
                if not title or not _is_relevant(title):
                    continue

                guid   = item.get("guid", "") or item.get("applicationLink", "")
                ext_id = "hm_" + str(guid)[-16:] if guid else "hm_" + str(hash(title))

                if ext_id in seen:
                    continue
                seen.add(ext_id)

                locations = item.get("locationRestrictions") or []
                location  = ", ".join(locations) if locations else "Worldwide / Remote"

                min_sal  = item.get("minSalary")
                max_sal  = item.get("maxSalary")
                currency = item.get("currency", "")
                salary   = f"{currency} {min_sal:,.0f} - {max_sal:,.0f}" if min_sal and max_sal else ""

                jobs.append({
                    "external_id": ext_id,
                    "platform":    "himalayas",
                    "title":       title,
                    "company":     item.get("companyName", ""),
                    "location":    location,
                    "salary":      salary,
                    "url":         item.get("applicationLink", ""),
                    "description": _clean_html(item.get("description", "") or item.get("excerpt", "")),
                    "job_type":    item.get("employmentType", "Full Time"),
                    "scraped_at":  datetime.utcnow().isoformat(),
                })

            time.sleep(1)

        except Exception as e:
            print(f"  Himalayas error for '{keyword}': {e}")
            continue

    print(f"  Himalayas: {len(jobs)} jobs scraped")
    return jobs
