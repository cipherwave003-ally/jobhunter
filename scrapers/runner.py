"""
Scraper runner — runs all enabled scrapers and returns combined results.
"""

from scrapers.remoteok import scrape as scrape_remoteok
from scrapers.linkedin import scrape as scrape_linkedin
from scrapers.himalayas import scrape as scrape_himalayas
from scrapers.greenhouse import scrape as scrape_greenhouse
from scrapers.weworkremotely import scrape as scrape_wwr
from scrapers.hivepro import scrape as scrape_hivepro


def run_all(max_per_source: int = 15) -> list:
    all_jobs = []

    print("\n[1/3] RemoteOK...")
    all_jobs += scrape_remoteok(max_results=max_per_source)

    print("\n[2/3] LinkedIn...")
    all_jobs += scrape_linkedin(max_results=max_per_source)

    print("\n[3/6] Himalayas...")
    all_jobs += scrape_himalayas(max_results=max_per_source)

    print("\n[4/6] Greenhouse (company boards)...")
    all_jobs += scrape_greenhouse(max_results=max_per_source * 2)

    print("\n[5/6] WeWorkRemotely...")
    all_jobs += scrape_wwr(max_results=max_per_source)

    print("\n[6/6] Hive Pro...")
    all_jobs += scrape_hivepro(max_results=max_per_source)

    # Deduplicate by external_id
    seen = set()
    unique = []
    for j in all_jobs:
        if j["external_id"] not in seen:
            seen.add(j["external_id"])
            unique.append(j)

    print(f"\n✓ Total unique jobs: {len(unique)}")
    return unique
