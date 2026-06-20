"""
deidentify_contributors.py
--------------------------
Turns the raw contributor scrape into a committed-safe, de-identified dataset.

What it does:
  - replaces each contributor's NAME with a salted hash (an internal id)
  - DROPS the verbatim bio and profile link (identifying free text)
  - KEEPS only structured, analyzable fields:
        contributor_id, credentials, years_experience,
        specialty_tags, article_count, first_article_date, last_article_date

Salting (why and how):
  A plain hash of a name is NOT safe on its own -- names come from a small,
  guessable space, so anyone could hash every plausible name and match it
  against contributor_id (a "rainbow table" attack). To prevent that, each
  name is combined with a random SECRET SALT before hashing:

        contributor_id = sha256(salt + name)[:12]

  The salt is generated once on first run and stored in salt.txt, which is
  LOCAL ONLY and listed in .gitignore -- it must never be committed. Without
  the salt, contributor_id cannot be reversed back to a name. The same salt
  is reused on every run, so a given contributor always maps to the same id
  (useful for linking/deduping) -- but only on this machine, since the salt
  never leaves it.

  Deleting salt.txt resets all ids (every name will hash differently next run).

Pipeline:
    scrape_contributors.py -> data/contributors_raw.csv          (local only)
    deidentify_contributors.py -> data/contributors_deidentified.csv  (committed)

Run:  python deidentify_contributors.py
"""

import os
import re
import secrets
import hashlib
import pandas as pd

RAW_PATH = os.path.join("data", "contributors_raw.csv")
OUT_PATH = os.path.join("data", "contributors_deidentified.csv")
SALT_PATH = "salt.txt"

# Sensitive columns that must NEVER appear in the committed output.
SENSITIVE_COLUMNS = ["name", "bio", "profile_link"]

# Keyword -> specialty tag. Matched (case-insensitive) against the bio text.
# Extend this list as you see more bios.
SPECIALTY_KEYWORDS = {
    "marriage": "marriage/family",
    "family": "marriage/family",
    "couples": "marriage/family",
    "trauma": "trauma",
    "anxiety": "anxiety",
    "depression": "depression",
    "anger": "anger management",
    "addiction": "addiction",
    "child": "children/adolescents",
    "adolescent": "children/adolescents",
    "coach": "coaching",
    "supervisor": "clinical supervision",
    "social work": "social work",
}


def get_salt() -> str:
    """Load the salt, or create one on first run and store it locally."""
    if os.path.exists(SALT_PATH):
        with open(SALT_PATH) as f:
            return f.read().strip()
    salt = secrets.token_hex(16)          # 32-char random secret
    with open(SALT_PATH, "w") as f:
        f.write(salt)
    print(f"Generated a new salt and saved it to {SALT_PATH} (keep this local).")
    return salt


def hash_name(name: str, salt: str) -> str:
    """Salted SHA-256 of the name, shortened to a 12-char id."""
    digest = hashlib.sha256((salt + str(name)).encode("utf-8")).hexdigest()
    return digest[:12]


def parse_years(bio: str) -> int | None:
    """
    Pull a years-of-experience number from free text.
    Catches patterns like '18 years', 'over 35 years', 'last 12 years'.
    Returns None if no number is stated (honest about missing data).
    """
    if not isinstance(bio, str):
        return None
    match = re.search(r"(\d+)\s+years", bio, flags=re.IGNORECASE)
    return int(match.group(1)) if match else None


def extract_specialties(bio: str) -> str:
    """Return a ';'-joined set of specialty tags found in the bio."""
    if not isinstance(bio, str):
        return ""
    found = []
    low = bio.lower()
    for keyword, tag in SPECIALTY_KEYWORDS.items():
        if keyword in low and tag not in found:
            found.append(tag)
    return "; ".join(found)


def main():
    if not os.path.exists(RAW_PATH):
        raise SystemExit(f"'{RAW_PATH}' not found. Run scrape_contributors.py first.")

    raw = pd.read_csv(RAW_PATH)
    salt = get_salt()

    out = pd.DataFrame()
    out["contributor_id"] = raw["name"].apply(lambda n: hash_name(n, salt))
    out["credentials"] = raw.get("credentials", "")
    out["years_experience"] = raw.get("bio", "").apply(parse_years)
    out["specialty_tags"] = raw.get("bio", "").apply(extract_specialties)
    out["article_count"] = raw.get("article_count", pd.NA)
    out["first_article_date"] = raw.get("first_article_date", pd.NA)
    out["last_article_date"] = raw.get("last_article_date", pd.NA)

    leaked = [c for c in SENSITIVE_COLUMNS if c in out.columns]
    if leaked:
        raise SystemExit(f"Refusing to write: sensitive columns present {leaked}")

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    out.to_csv(OUT_PATH, index=False)

    n = len(out)
    yrs = out["years_experience"].notna().sum()
    print(f"Wrote {n} de-identified contributor rows to {OUT_PATH}")
    print(f"Columns: {list(out.columns)}")
    print(f"Years-of-experience stated for {yrs} of {n} contributors.")


if __name__ == "__main__":
    main()