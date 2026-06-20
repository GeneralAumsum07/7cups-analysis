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
    
    base_url = "https://www.7cups.com/"
    start_url = "https://www.7cups.com/qa/"

    all_threads = []

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=False
        )

        page = browser.new_page()

        print(f"Opening {start_url}")

        page.goto(start_url)

        page.wait_for_selector("div.card.mb-3")

        cards = page.query_selector_all("div.card.mb-3")

        recent_card = None

        for card in cards:
            header = card.query_selector(".card-header")

            if header:
                header_text = header.inner_text().strip()

                if "Recent Questions" in header_text:
                    recent_card = card
                    break

        if recent_card is None:
            browser.close()
            raise Exception("Could not locate the 'Recent Questions' section.")

        thread_elements = recent_card.query_selector_all(
            ".list-group.list-group-flush > a.list-group-item"
        )

        print(f"Found {len(thread_elements)} recent questions.\n")

        for thread in thread_elements:

            # -----------------------
            # Title
            # -----------------------

            title_element = thread.query_selector(".fw-semibold")

            if not title_element:
                continue

            title = title_element.inner_text().strip()

            # -----------------------
            # Date
            # -----------------------

            date_element = thread.query_selector("span.me-3 span")

            if not date_element:
                continue

            date = date_element.inner_text().strip()

            # -----------------------
            # Link
            # -----------------------

            href = thread.get_attribute("href")

            if href:

                if href.startswith("/"):
                    full_link = base_url + href
                else:
                    full_link = href

            else:
                full_link = ""

            all_threads.append({
                "title": title,
                "date": date,
                "link": full_link
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