"""
infosec-jobs.com Scraper — cybersecurity specific job board.
No auth needed, no bot protection.
"""

import re
import time
import hashlib
import requests
from datetime import datetime
from bs4 import BeautifulSoup

BASE_URL = "https://infosec-jobs.com"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
}

SEARCHES = [
    "cybersecurity analyst",
    "security engineer",
    "soc analyst",
    "detection engineer",
    "penetration tester",
    "incident response",
    "cloud security",
]

TITLE_MUST = [
    "security", "cyber", "soc", "penetration", "vulnerability",
    "forensic", "threat", "incident", "devsecops", "infosec",
    "appsec", "detection", "cloud security", "grc", "compliance"
]

TITLE_EXCLUDE = [
    "intern", "fresher", "director", "vp ", "vice president",
    "head of", "chief", "junior", "manager", "principal", "staff",
    "lead", "accounting", "finance", "linux system admin"
]

LOCATION_PREFER = [
    "india", "bengaluru", "bangalore", "mumbai", "hyderabad",
    "chennai", "remote", "pune"
]


def _job_id(url: str) -> str:
    return "ij_" + hashlib.md5(url.encode()).hexdigest()[:12]


def _is_relevant(title: str) -> bool:
    t = title.lower()
    if any(x in t for x in TITLE_EXCLUDE):
        return False
    for k in TITLE_MUST:
        if re.search(r"\b" + re.escape(k) + r"\b", t):
            return True
    return False


def _is_preferred_location(text: str) -> bool:
    t = text.lower()
    return any(loc in t for loc in LOCATION_PREFER)


def _fetch_description(url: str) -> str:
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        if resp.status_code != 200:
            return ""
        soup = BeautifulSoup(resp.text, "html.parser")
        desc = soup.find("div", {"class": "job-description"})
        if not desc:
            desc = soup.find("div", {"itemprop": "description"})
        if not desc:
            desc = soup.find("main")
        return desc.get_text(separator="\n").strip()[:4000] if desc else ""
    except Exception:
        return ""


def scrape(max_results: int = 20) -> list:
    jobs = []
    seen = set()

    for keyword in SEARCHES:
        if len(jobs) >= max_results:
            break

        url = f"{BASE_URL}/?s={keyword.replace(' ', '+')}"

        try:
            resp = requests.get(url, headers=HEADERS, timeout=12)
            if resp.status_code != 200:
                print(f"  ⚠ infosec-jobs: status {resp.status_code} for {keyword}")
                continue

            soup = BeautifulSoup(resp.text, "html.parser")
            links = soup.find_all("a", href=True)
            job_links = [a for a in links if "/job/" in a.get("href", "")]

            print(f"  {len(job_links)} listings for '{keyword}'")

            for a in job_links:
                if len(jobs) >= max_results:
                    break

                title = a.get_text().strip()
                href  = a.get("href", "")
                if not href.startswith("http"):
                    href = BASE_URL + href

                if not title or not _is_relevant(title):
                    continue

                ext_id = _job_id(href)
                if ext_id in seen:
                    continue
                seen.add(ext_id)

                # Extract location from URL slug
                location = ""
                parts = href.split("-")
                for loc in LOCATION_PREFER:
                    if loc in href.lower():
                        location = loc.capitalize()
                        break
                if not location:
                    location = "See listing"

                job = {
                    "external_id": ext_id,
                    "platform":    "infosec-jobs",
                    "title":       title,
                    "company":     "",
                    "location":    location,
                    "salary":      "",
                    "url":         href,
                    "description": _fetch_description(href),
                    "job_type":    "full-time",
                    "scraped_at":  datetime.utcnow().isoformat(),
                }

                jobs.append(job)
                time.sleep(0.5)

            time.sleep(1.5)

        except Exception as e:
            print(f"  ⚠ infosec-jobs error for {keyword}: {e}")
            continue

    print(f"  ✓ infosec-jobs: {len(jobs)} jobs scraped")
    return jobs
