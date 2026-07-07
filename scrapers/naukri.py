"""
Naukri.com Scraper — uses Playwright to handle JS-rendered content.
"""

import time
import hashlib
from datetime import datetime
from playwright.sync_api import sync_playwright, TimeoutError as PW_Timeout

SEARCHES = [
    ("cybersecurity analyst", "bangalore"),
    ("security engineer", "bangalore"),
    ("soc analyst", "bangalore"),
    ("penetration tester", "india"),
    ("incident response", "india"),
    ("detection engineer", "india"),
]

TITLE_MUST = [
    "security", "cyber", "soc", "penetration", "vulnerability",
    "forensic", "threat", "incident", "devsecops", "infosec",
    "appsec", "detection", "cloud security"
]

TITLE_EXCLUDE = [
    "intern", "fresher", "director", "vp ", "vice president",
    "head of", "chief", "junior", "0-1 year", "officer", "guard",
    "physical security"
]


def _job_id(url: str) -> str:
    return "nk_" + hashlib.md5(url.encode()).hexdigest()[:12]


def _is_relevant(title: str) -> bool:
    t = title.lower()
    if any(x in t for x in TITLE_EXCLUDE):
        return False
    return any(k in t for k in TITLE_MUST)


def scrape(max_results: int = 20) -> list:
    jobs = []
    seen = set()

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-blink-features=AutomationControlled"],
        )
        ctx = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1280, "height": 900},
        )
        page = ctx.new_page()

        for keyword, location in SEARCHES:
            if len(jobs) >= max_results:
                break

            url = (
                f"https://www.naukri.com/{keyword.replace(' ', '-')}"
                f"-jobs-in-{location}?experience=2&experience=5"
            )

            try:
                page.goto(url, timeout=20000)
                time.sleep(3)

                # Wait for job cards to appear
                page.wait_for_selector(
                    ".srp-jobtuple-wrapper, .jobTuple, article.jobTuple",
                    timeout=10000
                )

                # Get all job card elements
                cards = page.query_selector_all(".srp-jobtuple-wrapper")
                if not cards:
                    cards = page.query_selector_all("article.jobTuple")

                print(f"  {len(cards)} cards for '{keyword}' in {location}")

                for card in cards:
                    if len(jobs) >= max_results:
                        break
                    try:
                        title_el   = card.query_selector("a.title")
                        company_el = card.query_selector("a.subTitle, .comp-name")
                        loc_el     = card.query_selector(".locWdth, .location")
                        sal_el     = card.query_selector(".sal-wrap, .salary")

                        if not title_el:
                            continue

                        title = title_el.inner_text().strip()
                        if not _is_relevant(title):
                            continue

                        href = title_el.get_attribute("href") or ""
                        if not href:
                            continue

                        ext_id = _job_id(href)
                        if ext_id in seen:
                            continue
                        seen.add(ext_id)

                        # Fetch description
                        desc = ""
                        try:
                            page.goto(href, timeout=12000)
                            time.sleep(1.5)
                            desc_el = page.query_selector(".job-desc, .dang-inner-html")
                            if desc_el:
                                desc = desc_el.inner_text().strip()[:4000]
                            page.go_back()
                            time.sleep(1)
                        except PW_Timeout:
                            pass

                        jobs.append({
                            "external_id": ext_id,
                            "platform":    "naukri",
                            "title":       title,
                            "company":     company_el.inner_text().strip() if company_el else "",
                            "location":    loc_el.inner_text().strip() if loc_el else location,
                            "salary":      sal_el.inner_text().strip() if sal_el else "",
                            "url":         href,
                            "description": desc,
                            "job_type":    "full-time",
                            "scraped_at":  datetime.utcnow().isoformat(),
                        })

                    except Exception:
                        continue

                time.sleep(2)

            except PW_Timeout:
                print(f"  ⚠ Naukri timeout: {keyword} in {location}")
                continue
            except Exception as e:
                print(f"  ⚠ Naukri error: {e}")
                continue

        browser.close()

    print(f"  ✓ Naukri: {len(jobs)} jobs scraped")
    return jobs
