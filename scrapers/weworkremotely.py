"""
WeWorkRemotely Scraper — public RSS feed, no login needed.
"""

import re
import time
import hashlib
import requests
from datetime import datetime
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}

FEEDS = [
    "https://weworkremotely.com/categories/all-other-remote-jobs.rss",
    "https://weworkremotely.com/categories/remote-devops-sysadmin-jobs.rss",
    "https://weworkremotely.com/remote-jobs.rss",
]

TITLE_MUST = [
    "security", "cyber", "soc", "penetration", "vulnerability",
    "forensic", "threat", "incident", "devsecops", "infosec",
    "appsec", "detection", "cloud security", "grc", "compliance"
]

TITLE_EXCLUDE = [
    "intern", "fresher", "director", "vp ", "vice president",
    "head of", "chief", "junior", "sales", "marketing", "recruiter"
]


def _job_id(url: str) -> str:
    return "wwr_" + hashlib.md5(url.encode()).hexdigest()[:12]


def _is_relevant(title: str) -> bool:
    import re as _re
    t = title.lower()
    if any(x in t for x in TITLE_EXCLUDE):
        return False
    # Use word-boundary matching to avoid "soc" matching inside "associate"
    for k in TITLE_MUST:
        if _re.search(r"\b" + _re.escape(k) + r"\b", t):
            return True
    return False


def _clean_description(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text(separator="\n").strip()[:4000]


def scrape(max_results: int = 20) -> list:
    jobs = []
    seen = set()

    for feed_url in FEEDS:
        if len(jobs) >= max_results:
            break

        try:
            resp = requests.get(feed_url, headers=HEADERS, timeout=12)
            if resp.status_code != 200:
                print(f"  ⚠ WWR: status {resp.status_code} for {feed_url}")
                continue

            soup = BeautifulSoup(resp.text, "xml")
            items = soup.find_all("item")
            print(f"  {len(items)} items from {feed_url.split('/')[-1]}")

            for item in items:
                if len(jobs) >= max_results:
                    break

                title_raw = item.find("title")
                link      = item.find("link")
                desc      = item.find("description")
                pub_date  = item.find("pubDate")

                if not title_raw or not link:
                    continue

                full_title = title_raw.get_text().strip()
                # WWR titles are "Company: Job Title"
                if ":" in full_title:
                    company, title = full_title.split(":", 1)
                    company = company.strip()
                    title   = title.strip()
                else:
                    company = ""
                    title   = full_title

                if not _is_relevant(title):
                    continue

                url = link.get_text().strip()
                ext_id = _job_id(url)
                if ext_id in seen:
                    continue
                seen.add(ext_id)

                description = _clean_description(desc.get_text()) if desc else ""

                job = {
                    "external_id": ext_id,
                    "platform":    "weworkremotely",
                    "title":       title,
                    "company":     company,
                    "location":    "Remote",
                    "salary":      "",
                    "url":         url,
                    "description": description,
                    "job_type":    "remote",
                    "scraped_at":  datetime.utcnow().isoformat(),
                }

                jobs.append(job)

            time.sleep(1)

        except Exception as e:
            print(f"  ⚠ WWR error for {feed_url}: {e}")
            continue

    print(f"  ✓ WeWorkRemotely: {len(jobs)} jobs scraped")
    return jobs
