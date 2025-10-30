# ABET Consolidation Tool — Consolidated Scraper

This repository contains utilities to parse ABET accreditation pages and extract
sectioned content and accordion entries. The goal is to consolidate workflow from
the original notebooks into a small, testable Python module.

Files added:
- `src/abet_scraper.py` — a reusable scraper module with functions to fetch pages,
  parse accordion items and extract content between H2 headers.
- `requirements.txt` — minimal dependencies (requests, beautifulsoup4, pytest).
  
Quick start
1. (Optional) Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run:

```bash
python3 scripts/run_scrape.py
```

# ABET-Consolidation-Tool-Team-1-
Capstone Project
