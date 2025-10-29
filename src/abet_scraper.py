"""ABET accreditation pages scraper utilities.

Provides small, testable functions to fetch a page, parse accordion entries
and extract sections between H2 headers. Designed to consolidate the logic
from the notebooks into a reusable module.

Contracts (short):
- fetch_page(url) -> str: HTML text or raises requests.HTTPError on non-200.
- parse_accordion_items(html) -> list[dict]: each dict has 'title' and 'html'.
- extract_between_h2(html, start_id, end_id=None) -> str: HTML between headers.

Error modes: network timeouts, missing elements return empty lists/strings.
"""
from typing import List, Dict, Optional
import requests
from bs4 import BeautifulSoup


def fetch_page(url: str, timeout: int = 10) -> str:
    """Fetch a URL and return the page HTML as text.

    Raises requests.RequestException on network errors and requests.HTTPError
    if a non-200 status code is returned.
    """
    resp = requests.get(url, timeout=timeout)
    resp.raise_for_status()
    return resp.text


def parse_accordion_items(html: str) -> List[Dict[str, str]]:
    """Parse accordion items (<li class="block-accordion-item">) from HTML.

    Returns a list of dicts: { 'title': <header text>, 'html': <inner html> }
    """
    soup = BeautifulSoup(html, "html.parser")
    items = []
    for li in soup.find_all('li', class_='block-accordion-item'):
        title_tag = li.find('h4', class_='accordion-header')
        title = title_tag.get_text(strip=True) if title_tag else ''
        # The inner content may be under a div with class 'accordion-content'
        content_div = li.find('div', class_='accordion-content')
        inner_html = content_div.decode_contents() if content_div else li.decode_contents()
        items.append({'title': title, 'html': inner_html})
    return items


def extract_between_h2(html: str, start_id: str, end_id: Optional[str] = None) -> str:
    """Extract HTML content between the H2 with id=start_id up to (but not including)
    the H2 with id=end_id. If end_id is None, extracts until the next H2 or end.

    Returns the concatenated inner HTML (as a string). If start header not found,
    returns an empty string.
    """
    soup = BeautifulSoup(html, "html.parser")
    start = soup.find('h2', id=str(start_id))
    if not start:
        return ''
    content = []
    sibling = start.find_next_sibling()
    while sibling:
        if sibling.name == 'h2' and end_id is not None and sibling.get('id') == str(end_id):
            break
        # stop if we reach the next h2 when end_id is None
        if sibling.name == 'h2' and end_id is None:
            break
        content.append(str(sibling))
        sibling = sibling.find_next_sibling()
    return ''.join(content)


def save_text_lines(lines: List[str], filepath: str) -> None:
    """Save a list of strings to a text file (one per line)."""
    with open(filepath, 'w', encoding='utf-8') as f:
        for line in lines:
            f.write(line.rstrip('\n') + '\n')


def extract_text_from_html(html: str) -> List[str]:
    """Return a cleaned list of text lines extracted from a fragment of HTML.

    Strips empty lines and returns sequential text nodes.
    """
    soup = BeautifulSoup(html, 'html.parser')
    texts = [t.strip() for t in soup.stripped_strings]
    return [t for t in texts if t]


def extract_first_ol_by_style(html: str, style_substring: str) -> List[str]:
    """Find the first <ol> whose style attribute contains style_substring
    and return its list item texts. If not found, return an empty list."""
    soup = BeautifulSoup(html, 'html.parser')
    ol = soup.find('ol', style=lambda s: s and style_substring in s)
    if not ol:
        return []
    return [li.get_text(strip=True) for li in ol.find_all('li')]


def find_ol_after_heading(html: str, heading_tag: str = 'h3', heading_id: Optional[str] = None,
                           heading_text_substring: Optional[str] = None) -> List[str]:
    """Find the first ordered list (<ol>) that appears after a heading.

    You can identify the heading either by id (heading_id) or by a substring of
    the heading text (heading_text_substring). Returns list of li texts or [] if
    not found.
    """
    soup = BeautifulSoup(html, 'html.parser')
    heading = None
    if heading_id:
        heading = soup.find(heading_tag, id=str(heading_id))
    elif heading_text_substring:
        # find heading with matching text
        for h in soup.find_all(heading_tag):
            if h.get_text(strip=True) and heading_text_substring in h.get_text(strip=True):
                heading = h
                break
    if not heading:
        return []
    # find next ol sibling or descendant after heading
    sib = heading.find_next_sibling()
    while sib:
        if sib.name == 'ol':
            return [li.get_text(strip=True) for li in sib.find_all('li')]
        # sometimes the ol is nested inside a div or other wrapper
        ol = sib.find('ol')
        if ol:
            return [li.get_text(strip=True) for li in ol.find_all('li')]
        sib = sib.find_next_sibling()
    return []


if __name__ == '__main__':
    # Simple CLI usage example (kept minimal so it can be used in notebooks or scripts)
    import argparse

    parser = argparse.ArgumentParser(description='Simple ABET page scraper utilities')
    parser.add_argument('url', help='ABET URL to fetch')
    parser.add_argument('--out', help='Output text file for extracted accordion titles', default='output.txt')
    args = parser.parse_args()

    html = fetch_page(args.url)
    items = parse_accordion_items(html)
    titles = [it['title'] for it in items]
    save_text_lines(titles, args.out)
    print(f'Wrote {len(titles)} accordion titles to {args.out}')
