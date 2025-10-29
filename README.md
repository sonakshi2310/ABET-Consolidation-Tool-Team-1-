# ABET Consolidation Tool — Consolidated Scraper

This repository contains utilities to parse ABET accreditation pages and extract
sectioned content and accordion entries. The goal is to consolidate workflow from
the original notebooks into a small, testable Python module.

Files added:
- `src/abet_scraper.py` — a reusable scraper module with functions to fetch pages,
  parse accordion items and extract content between H2 headers.
- `requirements.txt` — minimal dependencies (requests, beautifulsoup4, pytest).
- `tests/test_abet_scraper.py` — pytest unit tests using a local HTML sample.

Quick start
1. (Optional) Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run tests:

```bash
pytest -q
```

Ideas / next steps
- Integrate both notebooks' unique parsing logic into the module (if CS notebook
  includes different selectors, add functions for that).
- Add a small CLI or entry-point that can target both CS and CSE and write
  consolidated outputs.
- Add integration tests that perform live fetches (behind a network flag) or
  cached HTML fixtures for larger coverage.
# ABET-Consolidation-Tool-Team-1-
Capstone Project
