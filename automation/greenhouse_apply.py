"""
Greenhouse Auto-Apply
Fills Greenhouse job application forms via Playwright.
"""

import time
import json
from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError as PW_Timeout

PROFILE_PATH = Path(__file__).parent.parent / "data" / "profile.json"


def _load_profile() -> dict:
    if PROFILE_PATH.exists():
        return json.loads(PROFILE_PATH.read_text())
    return {}


def _fill(page, selectors, value):
    if not value:
        return
    for sel in selectors.split(","):
        try:
            el = page.query_selector(sel.strip())
            if el and el.is_visible():
                current = el.evaluate("e => e.value")
                if not current:
                    el.fill(value)
                return
        except Exception:
            continue


def apply(job: dict, cover_letter: str) -> dict:
    profile = _load_profile()
    url     = job.get("url", "")
    if not url:
        return {"success": False, "notes": "No URL"}

    name_parts = profile.get("name", "").split()
    first_name = name_parts[0] if name_parts else ""
    last_name  = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, args=["--no-sandbox"])
        page    = browser.new_page(viewport={"width": 1280, "height": 900})

        try:
            page.goto(url, timeout=20000)
            time.sleep(2)

            _fill(page, 'input[id*="first_name"], input[name*="first_name"]', first_name)
            _fill(page, 'input[id*="last_name"], input[name*="last_name"]', last_name)
            _fill(page, 'input[type="email"]', profile.get("email", ""))
            _fill(page, 'input[type="tel"]', profile.get("phone", ""))
            _fill(page, 'input[id*="linkedin"]', profile.get("linkedin_url", ""))
            _fill(page, 'input[id*="website"]', profile.get("portfolio_url", "") or profile.get("github_url", ""))

            for sel in ['textarea[id*="cover"]', 'textarea[name*="cover"]', 'textarea']:
                el = page.query_selector(sel)
                if el and el.is_visible():
                    val = el.evaluate("e => e.value")
                    if not val:
                        el.fill(cover_letter[:3000])
                    break

            resume_path = profile.get("resume_path", "")
            if resume_path and Path(resume_path).exists():
                fi = page.query_selector('input[type="file"]')
                if fi:
                    fi.set_input_files(resume_path)
                    time.sleep(1)
                    print("  Resume uploaded")

            page.screenshot(path="data/greenhouse_prefilled.png")
            print("  Form pre-filled. You have 5 minutes to review and submit.")
            print("  The browser will stay open — close it manually when done.")
            # Keep browser open for 5 minutes
            import time as _time
            for i in range(60):
                _time.sleep(5)
                try:
                    _ = page.url  # check if browser still open
                except Exception:
                    break  # browser was closed by user
            browser.close()
            return {"success": True, "notes": "Form pre-filled"}

        except PW_Timeout:
            browser.close()
            return {"success": False, "notes": "Timeout"}
        except Exception as e:
            browser.close()
            return {"success": False, "notes": str(e)}
