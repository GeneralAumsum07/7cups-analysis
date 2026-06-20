"""
scrape_contributors.py
----------------------
Collects the 7 Cups "Expert Contributors" sample (first 2 catalog pages),
then visits each contributor's profile for richer fields.

Output (raw, LOCAL ONLY -- gitignored):
    data/contributors_raw.csv
    columns: name, credentials, bio, profile_link,
             article_count, first_article_date, last_article_date

This raw file is the input to deidentify_contributors.py, which hashes the
name (salted), drops the bio, and writes the committed-safe dataset.

Notes on the page structure (from inspection):
  Catalog (/advice/catalog/contributors/):
    - results live in  #results-container
    - each profile link is  a.streched-link  (note the site's misspelling)
    - pagination is JavaScript-driven: the URL does NOT change, so we must
      CLICK the page-2 button rather than request a page-2 URL.
  Profile (/advice/@handle):
    - name + credentials in  h1.fw-semibold  (split on first comma)
    - bio in  h5.text-muted
    - article cards in  #article-container .card
    - each card's date in  div.fw-semibold.small  ("Posted 12 August 2019")

Run:  python scrape_contributors.py
"""

import os
import re
import time
from datetime import datetime

import pandas as pd
from playwright.sync_api import sync_playwright

CATALOG_URL = "https://www.7cups.com/advice/catalog/contributors/"
BASE = "https://www.7cups.com"
PAGES_TO_SCRAPE = 2
OUT_PATH = os.path.join("data", "contributors_raw.csv")


# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------
def parse_posted_date(text: str):
    if not text:
        return None
    cleaned = text.replace("Posted", "").strip()
    try:
        return datetime.strptime(cleaned, "%d %B %Y").date().isoformat()
    except ValueError:
        return None


def split_name_credentials(heading: str):
    if "," in heading:
        name, creds = heading.split(",", 1)
        return name.strip(), creds.strip()
    return heading.strip(), ""


# ----------------------------------------------------------------------
# Phase 1: collect profile links across the first N catalog pages
# ----------------------------------------------------------------------
def collect_profile_links(page) -> list[str]:
    page.goto(CATALOG_URL)
    page.wait_for_selector("#results-container a.streched-link")

    all_hrefs = []

    for page_num in range(1, PAGES_TO_SCRAPE + 1):
        links = page.query_selector_all("#results-container a.streched-link")
        hrefs = [a.get_attribute("href") for a in links]
        hrefs = [h for h in hrefs if h]  # drop any None
        print(f"  Catalog page {page_num}: found {len(hrefs)} contributor links")
        all_hrefs.extend(hrefs)

        if page_num < PAGES_TO_SCRAPE:
            next_num = page_num + 1

            before = page.query_selector("#results-container").inner_text()

            next_btn = page.query_selector(f"a.page-link[aria-label='Page {next_num}']")

            if not next_btn:
                print(f"  Could not find pager button for page {next_num}; stopping.")
                break

            next_btn.click()

            new_loaded = False
            for _ in range(50):  # up to ~10 seconds
                time.sleep(0.2)
                container = page.query_selector("#results-container")
                if container is None:
                    continue  # mid-rebuild; keep waiting
                after = container.inner_text()
                if after and after != before:
                    new_loaded = True
                    break

            if not new_loaded:
                print(f"  Page {next_num} did not refresh in time; "
                      f"continuing with what loaded.")

            page.wait_for_selector("#results-container a.streched-link")

    seen, unique = set(), []
    for h in all_hrefs:
        if h not in seen:
            seen.add(h)
            unique.append(h)
    print(f"  Total unique profiles: {len(unique)}")
    return unique


# ----------------------------------------------------------------------
# Phase 2: visit each profile and pull the fields
# ----------------------------------------------------------------------
def scrape_profile(page, href: str) -> dict:
    url = href if href.startswith("http") else BASE + href
    page.goto(url)
    page.wait_for_selector("h1.fw-semibold")

    heading = page.query_selector("h1.fw-semibold").inner_text().strip()
    name, credentials = split_name_credentials(heading)

    bio_el = page.query_selector("h5.text-muted")
    bio = bio_el.inner_text().strip() if bio_el else ""

    cards = page.query_selector_all("#article-container .card")
    article_count = len(cards)

    dates = []
    for card in cards:
        date_el = card.query_selector(".fw-semibold.small")
        if date_el:
            d = parse_posted_date(date_el.inner_text())
            if d:
                dates.append(d)

    first_date = min(dates) if dates else None
    last_date = max(dates) if dates else None

    return {
        "name": name,
        "credentials": credentials,
        "bio": bio,
        "profile_link": url,
        "article_count": article_count,
        "first_article_date": first_date,
        "last_article_date": last_date,
    }


# ----------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------
def main():
    rows = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        print("Phase 1: collecting profile links...")
        links = collect_profile_links(page)

        print("\nPhase 2: scraping each profile...")
        for i, href in enumerate(links, 1):
            try:
                data = scrape_profile(page, href)
                rows.append(data)
                print(f"  [{i}/{len(links)}] {data['name']} "
                      f"({data['article_count']} articles)")
            except Exception as e:
                print(f"  [{i}/{len(links)}] failed on {href}: {e}")
            time.sleep(0.5)

        browser.close()

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    df = pd.DataFrame(rows)
    df.to_csv(OUT_PATH, index=False)
    print(f"\nDone. Wrote {len(df)} contributors to {OUT_PATH}")


if __name__ == "__main__":
    main()