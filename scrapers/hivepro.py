"""
Hive Pro Careers Scraper — uses Playwright (Zoho Recruit JS-rendered page).
Single company source — cybersecurity company (CTEM/exposure management).
"""

import re
import time
import hashlib
from datetime import datetime
from playwright.sync_api import sync_playwright, TimeoutError as PW_Timeout

CAREERS_URL = "https://careers.hivepro.com/jobs/Careers"

TITLE_EXCLUDE = [
    "intern", "fresher", "sales", "marketing", "hr ", "finance",
    "accounting", "recruiter", "office"
]


def _job_id(url: str) -> str:
    return "hp_" + hashlib.md5(url.encode()).hexdigest()[:12]


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
            viewport={"width": 1280, "height": 900},
        )
        page = ctx.new_page()

        try:
            page.goto(CAREERS_URL, timeout=20000)
            time.sleep(3)

            # Zoho Recruit job listings typically render as links or list items
            # Try several common selector patterns
            selectors = [
                "a[href*='/jobs/']",
                ".job-listing a",
                "[class*='job'] a",
                "tr a",
            ]

            links = []
            for sel in selectors:
                found = page.query_selector_all(sel)
                if found:
                    links = found
                    print(f"  Found {len(found)} elements with selector: {sel}")
                    break

            if not links:
                print("  ⚠ Hive Pro: no job links found with any selector")
                browser.close()
                return []

            for link in links:
                if len(jobs) >= max_results:
                    break
                try:
                    title = link.inner_text().strip()
                    href  = link.get_attribute("href") or ""

                    if not title or not href:
                        continue
                    if not _is_relevant(title):
                        continue

                    if not href.startswith("http"):
                        href = "https://careers.hivepro.com" + href

                    ext_id = _job_id(href)
                    if ext_id in seen:
                        continue
                    seen.add(ext_id)

                    jobs.append({
                        "external_id": ext_id,
                        "platform":    "hivepro",
                        "title":       title,
                        "company":     "Hive Pro",
                        "location":    "See listing",
                        "salary":      "",
                        "url":         href,
                        "description": "",
                        "job_type":    "full-time",
                        "scraped_at":  datetime.utcnow().isoformat(),
                    })

                except Exception:
                    continue

            # Fetch descriptions for found jobs
            for job in jobs:
                try:
                    page.goto(job["url"], timeout=12000)
                    time.sleep(1.5)
                    desc_el = page.query_selector("[class*='description'], .job-description, main")
                    if desc_el:
                        job["description"] = desc_el.inner_text().strip()[:4000]
                except PW_Timeout:
                    pass
                except Exception:
                    pass

        except PW_Timeout:
            print("  ⚠ Hive Pro: page load timeout")
        except Exception as e:
            print(f"  ⚠ Hive Pro error: {e}")
        finally:
            browser.close()

    print(f"  ✓ Hive Pro: {len(jobs)} jobs scraped")
    return jobs
