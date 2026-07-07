"""
Wellfound Scraper — uses Playwright on role-specific search pages.
"""

import re
import time
import hashlib
from datetime import datetime
from playwright.sync_api import sync_playwright, TimeoutError as PW_Timeout

BASE_URL = "https://wellfound.com"

ROLE_SLUGS = [
    "cybersecurity",
    "cybersecurity-engineer",
    "cyber-security-analyst",
    "cyber-security-specialist",
]

TITLE_EXCLUDE = [
    "intern", "fresher", "sales partner", "commission-only",
    "business sales", "director", "vp ", "head of"
]


def _job_id(url: str) -> str:
    return "wf_" + hashlib.md5(url.encode()).hexdigest()[:12]


def _is_relevant(title: str) -> bool:
    t = title.lower()
    return not any(x in t for x in TITLE_EXCLUDE)


def scrape(max_results: int = 15) -> list:
    jobs = []
    seen = set()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
        ctx = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1280, "height": 1000},
        )
        page = ctx.new_page()

        for slug in ROLE_SLUGS:
            if len(jobs) >= max_results:
                break

            url = f"{BASE_URL}/role/r/{slug}"

            try:
                page.goto(url, timeout=20000)
                time.sleep(3)

                # Scroll to trigger lazy loading
                for _ in range(2):
                    page.keyboard.press("End")
                    time.sleep(1.5)

                # Job titles on Wellfound are typically in styled links/headings
                cards = page.query_selector_all("[data-test='StartupResult'], .styles_jobListing, [class*='job']")
                if not cards:
                    # Fallback: find any links that look like job postings
                    cards = page.query_selector_all("a[href*='/jobs/']")

                print(f"  {len(cards)} elements found for slug '{slug}'")

                for card in cards:
                    if len(jobs) >= max_results:
                        break
                    try:
                        title = card.inner_text().strip().split("\n")[0]
                        href  = card.get_attribute("href") or ""

                        if not href:
                            link_el = card.query_selector("a[href*='/jobs/']")
                            href = link_el.get_attribute("href") if link_el else ""

                        if not title or not href:
                            continue
                        if not _is_relevant(title):
                            continue

                        if not href.startswith("http"):
                            href = BASE_URL + href

                        ext_id = _job_id(href)
                        if ext_id in seen:
                            continue
                        seen.add(ext_id)

                        jobs.append({
                            "external_id": ext_id,
                            "platform":    "wellfound",
                            "title":       title[:120],
                            "company":     "",
                            "location":    "See listing",
                            "salary":      "",
                            "url":         href,
                            "description": "",
                            "job_type":    "full-time",
                            "scraped_at":  datetime.utcnow().isoformat(),
                        })

                    except Exception:
                        continue

                time.sleep(1.5)

            except PW_Timeout:
                print(f"  ⚠ Wellfound timeout for slug: {slug}")
                continue
            except Exception as e:
                print(f"  ⚠ Wellfound error for {slug}: {e}")
                continue

        browser.close()

    print(f"  ✓ Wellfound: {len(jobs)} jobs scraped")
    return jobs
