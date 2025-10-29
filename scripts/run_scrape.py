"""Run a quick scrape for CS and CSE pages and write outputs to text files.

This script uses the `src.abet_scraper` helpers added earlier. It's intended as
an integration smoke test to verify the notebooks' updated logic and produce
the same output files the notebooks used to create.
"""
import os
import sys

# ensure repository root is on sys.path so `src` package can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.abet_scraper import (
    fetch_page,
    extract_first_ol_by_style,
    parse_accordion_items,
    extract_text_from_html,
    save_text_lines,
)


def scrape_cs():
    url = 'https://www.abet.org/accreditation/accreditation-criteria/criteria-for-accrediting-computing-programs-2025-2026/'
    print('Fetching CS page...')
    html = fetch_page(url)
    cs_items = extract_first_ol_by_style(html, 'decimal')
    print(f'CS: extracted {len(cs_items)} items')
    save_text_lines(cs_items, 'CS_datafile.txt')
    return cs_items


def scrape_cse():
    url = 'https://www.abet.org/accreditation/accreditation-criteria/criteria-for-accrediting-engineering-programs-2025-2026/'
    print('Fetching CSE page...')
    html = fetch_page(url)
    items = parse_accordion_items(html)
    # find the Systems program
    target_title = 'Systems and Similarly Named Engineering Programs'
    target = next((it for it in items if it['title'] == target_title), None)
    if not target:
        print('CSE: target accordion item not found')
        save_text_lines([], 'CSE_datafile.txt')
        return []
    lines = extract_text_from_html(target['html'])
    save_text_lines(lines, 'CSE_datafile.txt')
    print(f'CSE: extracted {len(lines)} lines for "{target_title}"')
    return lines


def main():
    cs = scrape_cs()
    print('\nCS preview (first 8 lines):')
    for i, line in enumerate(cs[:8], start=1):
        print(f'{i}. {line}')

    cse = scrape_cse()
    print('\nCSE preview (first 12 lines):')
    for i, line in enumerate(cse[:12], start=1):
        print(f'{i}. {line}')


if __name__ == '__main__':
    main()
