# 7 Cups Public Data Analysis

A research project exploring publicly available data from [7 Cups](https://www.7cups.com), an online emotional-support and peer-listening platform. This work is part of a research opportunity at Mahindra University.

## Project Goal

Collect and analyze publicly available data to surface interesting patterns using a mix of techniques:

- Web scraping and data collection
- Graph analytics (e.g., networks linking contributors, specialties, or topics)
- Natural Language Processing (NLP)
- Data visualization and exploratory analysis

## Ethical Considerations

7 Cups is a mental-health support platform, so this project treats the data with extra care:

- **Public data only.** No logins, no private chats, no API endpoints. Only pages that are publicly accessible and permitted by the site's `robots.txt`.
- **De-identification.** For the contributors dataset, names are replaced with a salted hash and the free-text bios are dropped before anything is committed; only structured fields (credentials, years of experience, specialties, article counts and dates) are stored. The raw scrape is never committed.
- **Aggregate reporting.** Results are reported as patterns and statistics, never as individual quotes tied to a person.
- **Limited, supervised collection.** Data is gathered with automated browser-based scraping (Playwright driving a real browser engine), restricted to a small public sample and carried out under faculty supervision.

## Tech Stack

- **Python 3**
- `playwright` — browser automation; renders JavaScript-dependent pages (replaced the initial `requests` + `beautifulsoup4` approach, which a JavaScript challenge page blocked)
- `pandas` — structuring and saving data

## Project Structure

```
7cups-analysis/
├── README.md
├── .gitignore
├── explore_sitemap.py             # initial forum/Q&A exploration (first attempt)
├── scrape_contributors.py         # Playwright scraper for Expert Contributors
├── deidentify_contributors.py     # raw scrape -> de-identified, committed-safe CSV
├── data/
│   ├── contributors_raw.csv           # raw scrape (local only, gitignored)
│   ├── contributors_deidentified.csv  # de-identified (committed)
│   └── forum_threads.csv              # raw scrape (first attempt, gitignored) 
└── report/                        # report and generated charts
```

`salt.txt` (used for hashing) is generated locally and is gitignored — it is never committed.

## Status

Forum/Q&A was a brief first attempt; the Expert Contributors directory is the main dataset. Collection and de-identification are in place — analysis and visualization are the next step.

## Setup

```bash
pip install playwright pandas
playwright install
```

## License

For academic and educational use.