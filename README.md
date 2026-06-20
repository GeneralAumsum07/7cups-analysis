# 7 Cups Forum Analysis
 
A research project exploring publicly available forum data from [7 Cups](https://www.7cups.com), an online emotional-support and peer-listening platform. This work is part of a research opportunity at Mahindra University.
 
## Project Goal
 
Collect and analyze publicly available forum data to surface interesting patterns using a mix of techniques:
 
- Web scraping and data collection
- Graph analytics (e.g., networks of who replies to whom)
- Natural Language Processing (NLP)
- Data visualization and exploratory analysis

## Ethical Considerations
 
7 Cups is a mental-health support platform, so this project treats the data with extra care:
 
- **Public data only.** No logins, no private chats, no API endpoints. Only forum pages that are publicly accessible and permitted by the site's `robots.txt`.
- **Anonymization.** Usernames are replaced with non-identifying IDs (e.g. `user_001`) before any data is stored or shared. Real handles are never published.
- **Aggregate reporting.** Results are reported as patterns and statistics, never as individual quotes tied to a person.
- **Limited, supervised collection.** Data is gathered with automated browser-based scraping (Playwright driving a real browser engine), restricted to a small public sample.
 
## Tech Stack
 
- **Python 3**
- `playwright` — browser automation; renders JavaScript-dependent pages (replaced the initial `requests` + `beautifulsoup4` approach, which a JavaScript challenge page blocked)
- `pandas` — structuring and saving data

## Project Structure

```
7cups-research/
├── README.md
├── .gitignore
├── explore_sitemap.py    # initial exploration of the forum sitemap
├── data/                 # collected data (CSV)
└── report/               # final 1-2 page report
```

## Status

Exploratory phase — understanding the platform structure and collecting a small sample.

## Setup

```bash
pip install beautifulsoup4 pandas
playwright install
```

## License

For academic and educational use.
