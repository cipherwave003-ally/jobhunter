"""
LinkedIn Scraper — uses public RSS feed, no login needed.
No credentials, no cookies, no bot detection issues.
"""

import re
import time
import hashlib
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}

SEARCHES = [
    ("cybersecurity analyst", "India"),
    ("security engineer", "India"),
    ("SOC analyst", "India"),
    ("penetration tester", "India"),
    ("incident response", "India"),
    ("cybersecurity engineer", "Bengaluru"),
]

TITLE_MUST = [
    "security", "cyber", "soc", "penetration", "vulnerability",
    "forensic", "threat", "incident", "devsecops", "infosec",
    "appsec", "detection engineer", "cloud security"
]

TITLE_EXCLUDE = [
    "intern", "fresher", "director", "vp ", "vice president",
    "head of", "chief", "junior", "0-1 year", "officer", "guard"
]


def _job_id(url: str) -> str:
    return "li_" + hashlib.md5(url.encode()).hexdigest()[:12]


def _is_relevant(title: str) -> bool:
    t = title.lower()
    if any(x in t for x in TITLE_EXCLUDE):
        return False
    for k in TITLE_MUST:
        if re.search(r"\b" + re.escape(k) + r"\b", t):
            return True
    return False


def _fetch_description(url: str) -> str:
    """Fetch job description from the LinkedIn job page."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        if resp.status_code != 200:
            return ""
        soup = BeautifulSoup(resp.text, "html.parser")
        desc = soup.find("div", {"class": "show-more-less-html__markup"})
        if not desc:
            desc = soup.find("div", {"class": "description__text"})
        return desc.get_text(separator="\n").strip()[:4000] if desc else ""
    except Exception:
        return ""


def scrape(max_results: int = 20) -> list:
    jobs = []
    seen = set()

    for keyword, location in SEARCHES:
        if len(jobs) >= max_results:
            break

        url = (
            f"https://www.linkedin.com/jobs/search/?keywords="
            f"{keyword.replace(' ', '%20')}"
            f"&location={location.replace(' ', '%20')}"
            f"&f_E=3,4&f_JT=F&sortBy=DD"
        )

        try:
            resp = requests.get(url, headers=HEADERS, timeout=10)
            if resp.status_code != 200:
                print(f"  ⚠ LinkedIn: status {resp.status_code} for {keyword}")
                continue

            soup = BeautifulSoup(resp.text, "html.parser")
            cards = soup.find_all("div", {"class": "base-card"})

            if not cards:
                cards = soup.find_all("li", {"class": "jobs-search__results-list"})

            for card in cards:
                if len(jobs) >= max_results:
                    break

                try:
                    title_el   = card.find("h3") or card.find("span", {"class": "sr-only"})
                    company_el = card.find("h4") or card.find("a", {"class": "hidden-nested-link"})
                    loc_el     = card.find("span", {"class": "job-search-card__location"})
                    link_el    = card.find("a", {"class": "base-card__full-link"})

                    if not title_el:
                        continue

                    title = title_el.get_text().strip()
                    if not _is_relevant(title):
                        continue

                    href = link_el.get("href", "").split("?")[0] if link_el else ""
                    if not href:
                        continue

                    ext_id = _job_id(href)
                    if ext_id in seen:
                        continue
                    seen.add(ext_id)

                    job = {
                        "external_id": ext_id,
                        "platform":    "linkedin",
                        "title":       title,
                        "company":     company_el.get_text().strip() if company_el else "",
                        "location":    loc_el.get_text().strip() if loc_el else location,
                        "url":         href,
                        "description": _fetch_description(href),
                        "job_type":    "full-time",
                        "scraped_at":  datetime.utcnow().isoformat(),
                    }

                    jobs.append(job)
                    time.sleep(1)  # polite delay between requests

                except Exception:
                    continue

            time.sleep(2)  # delay between searches

        except Exception as e:
            print(f"  ⚠ LinkedIn error for {keyword}: {e}")
            continue

    print(f"  ✓ LinkedIn: {len(jobs)} jobs scraped")
    return jobs
