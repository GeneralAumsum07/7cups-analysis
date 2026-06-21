"""
analyze_contributors.py
-----------------------
Analysis + visualization of the de-identified Expert Contributors dataset.

Runs four analyses on data/contributors_deidentified.csv:
  1. Article output      -> mean / median / mode + histogram
  2. Credentials         -> frequency of each qualification + bar chart
  3. Specialties         -> frequency + a contributor<->specialty graph
  4. Years of experience -> median + histogram (with coverage note)

All charts are saved into report/. No identifying data is used -- only the
structured, de-identified fields.

Run:  python analyze_contributors.py
"""

import os
from collections import Counter

import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx

IN_PATH = os.path.join("data", "contributors_deidentified.csv")
REPORT_DIR = "report"


def save(fig_name):
    """Save the current matplotlib figure into report/ and close it."""
    os.makedirs(REPORT_DIR, exist_ok=True)
    path = os.path.join(REPORT_DIR, fig_name)
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"  saved {path}")


# ----------------------------------------------------------------------
# 1. Article output statistics
# ----------------------------------------------------------------------
def analyze_articles(df):
    print("\n[1] Article output")
    counts = df["article_count"].dropna()

    mean = counts.mean()
    median = counts.median()
    mode = counts.mode().tolist()   # mode() returns all most-common values

    print(f"  n = {len(counts)} contributors")
    print(f"  mean   = {mean:.2f}")
    print(f"  median = {median:.1f}")
    print(f"  mode   = {mode}")
    print(f"  range  = {int(counts.min())}-{int(counts.max())}")

    plt.figure(figsize=(8, 4.5))
    bins = range(int(counts.min()), int(counts.max()) + 2)
    plt.hist(counts, bins=bins, align="left", color="#3b6ea5", edgecolor="black")
    plt.xlabel("Articles published")
    plt.ylabel("Number of contributors")
    plt.title("Distribution of Article Output per Contributor")
    plt.xticks(range(int(counts.min()), int(counts.max()) + 1))
    save("article_count_hist.png")


# ----------------------------------------------------------------------
# 2. Credentials distribution
# ----------------------------------------------------------------------
def analyze_credentials(df):
    print("\n[2] Credentials")
    counter = Counter()
    for cred in df["credentials"].dropna():
        # credentials come comma-separated, e.g. "PhD, MFT"
        for part in str(cred).split(","):
            part = part.strip()
            if part:
                counter[part] += 1

    if not counter:
        print("  no credentials found")
        return

    for cred, n in counter.most_common():
        print(f"  {cred:<25} {n}")

    items = counter.most_common()
    labels = [c for c, _ in items][::-1]
    values = [n for _, n in items][::-1]

    plt.figure(figsize=(8, 5))
    plt.barh(labels, values, color="#3b6ea5", edgecolor="black")
    plt.xlabel("Number of contributors")
    plt.title("Credential Frequency Among Contributors")
    plt.xticks(range(0, max(values) + 1))
    save("credentials_dist.png")


# ----------------------------------------------------------------------
# 3. Specialties: distribution + contributor<->specialty graph
# ----------------------------------------------------------------------
def analyze_specialties(df):
    print("\n[3] Specialties")
    counter = Counter()
    edges = []   # (contributor_id, specialty) for the graph

    for _, row in df.iterrows():
        tags = row["specialty_tags"]
        if pd.isna(tags) or not str(tags).strip():
            continue
        for tag in str(tags).split(";"):
            tag = tag.strip()
            if tag:
                counter[tag] += 1
                edges.append((row["contributor_id"], tag))

    if not counter:
        print("  no specialties found")
        return

    for tag, n in counter.most_common():
        print(f"  {tag:<22} {n}")

    # --- bar chart ---
    items = counter.most_common()
    labels = [t for t, _ in items][::-1]
    values = [n for _, n in items][::-1]

    plt.figure(figsize=(8, 5))
    plt.barh(labels, values, color="#5a9367", edgecolor="black")
    plt.xlabel("Number of contributors")
    plt.title("Specialty Areas Among Contributors")
    plt.xticks(range(0, max(values) + 1))
    save("specialty_dist.png")

    # --- bipartite contributor <-> specialty graph ---
    G = nx.Graph()
    specialties = set(t for _, t in edges)
    contributors = set(c for c, _ in edges)
    G.add_nodes_from(specialties, kind="specialty")
    G.add_nodes_from(contributors, kind="contributor")
    G.add_edges_from(edges)

    pos = nx.spring_layout(G, k=0.6, seed=42)
    plt.figure(figsize=(11, 8))

    # specialty nodes: larger, labeled, green; contributor nodes: small, grey
    nx.draw_networkx_nodes(G, pos, nodelist=list(specialties),
                           node_color="#5a9367", node_size=1400)
    nx.draw_networkx_nodes(G, pos, nodelist=list(contributors),
                           node_color="#cccccc", node_size=300)
    nx.draw_networkx_edges(G, pos, alpha=0.4)
    nx.draw_networkx_labels(G, pos,
                            labels={t: t for t in specialties}, font_size=9)
    plt.title("Contributor \u2194 Specialty Network")
    plt.axis("off")
    save("specialty_graph.png")


# ----------------------------------------------------------------------
# 4. Years of experience
# ----------------------------------------------------------------------
def analyze_experience(df):
    print("\n[4] Years of experience")
    yrs = df["years_experience"].dropna()
    total = len(df)
    stated = len(yrs)

    print(f"  stated for {stated} of {total} contributors")
    if stated == 0:
        print("  nothing to plot")
        return
    print(f"  median = {yrs.median():.1f} years")
    print(f"  range  = {int(yrs.min())}-{int(yrs.max())} years")

    plt.figure(figsize=(8, 4.5))
    plt.hist(yrs, bins=range(0, int(yrs.max()) + 6, 5),
             color="#a05a8c", edgecolor="black")
    plt.xlabel("Years of experience")
    plt.ylabel("Number of contributors")
    plt.title(f"Years of Experience (stated for {stated} of {total})")
    save("experience_hist.png")


def main():
    if not os.path.exists(IN_PATH):
        raise SystemExit(f"'{IN_PATH}' not found. Run the pipeline first.")
    df = pd.read_csv(IN_PATH)
    print(f"Loaded {len(df)} contributors from {IN_PATH}")

    analyze_articles(df)
    analyze_credentials(df)
    analyze_specialties(df)
    analyze_experience(df)
    print("\nDone. Charts are in the report/ folder.")


if __name__ == "__main__":
    main()