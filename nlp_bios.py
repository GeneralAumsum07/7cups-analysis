"""
nlp_bios.py
-----------
A simple NLP pass over the contributor bios: tokenize -> remove stopwords ->
count word frequency across all bios combined.

This is the NLP step the project uses. It runs on the RAW file
(data/contributors_raw.csv), which is local-only and still contains the bio
text. The OUTPUT is aggregate -- a combined word count across all bios, not
tied to any individual -- so it is safe to commit.

Privacy choice: words occurring fewer than MIN_COUNT times are dropped. This
removes noise AND avoids surfacing rare, one-off tokens (names, places, book
titles) that could be identifying. Only recurring, thematic words remain.

Outputs:
    data/bio_word_frequency.csv
    report/bio_word_frequency.png  (bar chart of the top words)

Run (after scraping):  python nlp_bios.py
"""

import os
import re
from collections import Counter

import pandas as pd
import matplotlib.pyplot as plt

RAW_PATH = os.path.join("data", "contributors_raw.csv")
CSV_OUT = os.path.join("data", "bio_word_frequency.csv")
FIG_OUT = os.path.join("report", "bio_word_frequency.png")

TOP_N = 20        # how many words to show in the chart
MIN_COUNT = 2     # drop words appearing fewer than this many times
MIN_LEN = 3       # drop very short tokens

# A compact English stopword list -- common function words that carry little
# topical meaning.
STOPWORDS = {
    "the", "a", "an", "and", "or", "but", "of", "to", "in", "on", "for",
    "with", "as", "is", "are", "was", "were", "be", "been", "being", "at",
    "by", "from", "that", "this", "these", "those", "it", "its", "he", "she",
    "they", "them", "his", "her", "their", "who", "has", "have", "had", "not",
    "also", "can", "will", "more", "over", "into", "about", "across", "both",
    "out", "up", "than", "so", "such", "which", "while", "where", "when",
    "what", "all", "any", "some", "each", "other", "has", "had", "been",
    "wants", "something", "various", "wide", "range", "role", "field",
}


def tokenize(text: str) -> list[str]:
    """Lowercase, split on non-letters, drop stopwords and short tokens."""
    if not isinstance(text, str):
        return []
    words = re.findall(r"[a-z]+", text.lower())   # letters only -> drops digits/punctuation
    return [w for w in words if len(w) >= MIN_LEN and w not in STOPWORDS]


def main():
    if not os.path.exists(RAW_PATH):
        raise SystemExit(
            f"'{RAW_PATH}' not found. This NLP step needs the RAW file "
            "(with bios), which is local-only. Run the scraper first."
        )

    df = pd.read_csv(RAW_PATH)
    if "bio" not in df.columns:
        raise SystemExit("No 'bio' column in the raw file.")

    # Count words across ALL bios combined.
    counter = Counter()
    n_bios = 0
    for bio in df["bio"].dropna():
        tokens = tokenize(bio)
        if tokens:
            n_bios += 1
            counter.update(tokens)

    # Keep only recurring words (noise + privacy filter).
    frequent = {w: c for w, c in counter.items() if c >= MIN_COUNT}
    freq_series = pd.Series(frequent).sort_values(ascending=False)

    print(f"Processed {n_bios} bios")
    print(f"Unique words (after stopwords): {len(counter)}")
    print(f"Words kept (count >= {MIN_COUNT}): {len(freq_series)}\n")
    print("Top words:")
    print(freq_series.head(TOP_N).to_string())

    os.makedirs(os.path.dirname(CSV_OUT), exist_ok=True)
    freq_series.rename("count").to_csv(CSV_OUT, index_label="word")

    # Bar chart of the top words.
    top = freq_series.head(TOP_N)
    os.makedirs(os.path.dirname(FIG_OUT), exist_ok=True)
    plt.figure(figsize=(8, 6))
    top.sort_values().plot(kind="barh", color="#c47e3b", edgecolor="black")
    plt.xlabel("Frequency across all bios")
    plt.title(f"Most Common Words in Contributor Bios (top {len(top)})")
    plt.tight_layout()
    plt.savefig(FIG_OUT, dpi=150)
    plt.close()

    print(f"\nSaved {CSV_OUT} and {FIG_OUT}")


if __name__ == "__main__":
    main()