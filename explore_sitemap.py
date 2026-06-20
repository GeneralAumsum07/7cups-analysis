"""
explore_sitemap.py
------------------
A Playwright script that scrapes
the list of recent forum questions from 7 cups.

It collects:
    - Question title
    - Date posted
    - Thread link

Run with:
    python explore_sitemap.py
"""
import os
from playwright.sync_api import sync_playwright
import pandas as pd


def scrape_sitemap():
    all_threads = []

    base_url = "https://www.7cups.com/"
    start_url = "https://www.7cups.com/qa/"

    with sync_playwright() as p:

        browser = p.chromium.launch(headless=False)

        page = browser.new_page()

        print(f"Opening {start_url}")

        page.goto(start_url)

        page.wait_for_selector("a.list-group-item")

        thread_elements = page.query_selector_all("a.list-group-item")

        for thread in thread_elements:

            # -----------------------------
            # Title
            # -----------------------------
            title_element = thread.query_selector(".fw-semibold")

            if title_element:
                title = title_element.inner_text().strip()
            else:
                title = ""

            # -----------------------------
            # Date
            # -----------------------------
            date_element = thread.query_selector("span.me-3 span")

            if date_element:
                date = date_element.inner_text().strip()
            else:
                date = ""

            # -----------------------------
            # Link
            # -----------------------------
            href = thread.get_attribute("href")

            if href:
                # Convert relative URL to absolute URL
                if href.startswith("/"):
                    full_link = base_url + href
                else:
                    full_link = href
            else:
                full_link = ""

            all_threads.append({
                "title": title,
                "date": date,
                "link": full_link,
            })

        browser.close()

    return all_threads


if __name__ == "__main__":

    threads = scrape_sitemap()

    df = pd.DataFrame(threads)

    os.makedirs("data", exist_ok=True)
    df.to_csv("data/forum_threads.csv", index=False)

    print(f"\nDone! Collected {len(df)} threads.")

    print("\nFirst few rows:\n")
    print(df.head())