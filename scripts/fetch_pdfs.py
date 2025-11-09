"""Fetch PDFs from URLs

Usage:
    python scripts/fetch_pdfs.py                    # Fetch default PDFs
    python scripts/fetch_pdfs.py --urls <url>...    # Fetch custom URLs
    python scripts/fetch_pdfs.py --no-text          # Skip text extraction
"""
import os
import sys
import argparse
import logging
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.abet_pdf_simple import get_pdf_from_url, read_pdf_text

DEFAULT_PDFS = [
    {"name": "CS_Criteria", "url": "https://www.abet.org/wp-content/uploads/2023/05/2024-2025_CAC_Criteria.pdf"},
    {"name": "CSE_Criteria", "url": "https://www.abet.org/wp-content/uploads/2023/05/2024-2025_EAC_Criteria.pdf"},
]


def setup_logging():
    os.makedirs('logs', exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[logging.FileHandler('logs/fetch_pdfs.log'), logging.StreamHandler()]
    )
    return logging.getLogger(__name__)


def fetch_pdf(url: str, name: str, pdf_dir: str, text_dir: str, extract_text: bool, logger):
    try:
        logger.info(f"Fetching {name}")
        pdf_bytes = get_pdf_from_url(url)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        os.makedirs(pdf_dir, exist_ok=True)
        pdf_path = os.path.join(pdf_dir, f"{name}_{timestamp}.pdf")
        with open(pdf_path, 'wb') as f:
            f.write(pdf_bytes)
        logger.info(f"Saved: {pdf_path}")
        
        if extract_text:
            os.makedirs(text_dir, exist_ok=True)
            text = read_pdf_text(pdf_bytes)
            text_path = os.path.join(text_dir, f"{name}_{timestamp}.txt")
            with open(text_path, 'w', encoding='utf-8') as f:
                f.write(text)
            logger.info(f"Saved text: {text_path}")
        return True
    except Exception as e:
        logger.error(f"Error: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description='Fetch PDFs from URLs')
    parser.add_argument('--urls', nargs='+', help='PDF URLs')
    parser.add_argument('--names', nargs='+', help='PDF names')
    parser.add_argument('--output-dir', default='data/abet_pdfs', help='PDF directory')
    parser.add_argument('--text-dir', default='data/abet_pdf_text', help='Text directory')
    parser.add_argument('--no-text', action='store_true', help='Skip text extraction')
    args = parser.parse_args()
    
    logger = setup_logging()
    
    if args.urls:
        names = args.names or [f'PDF_{i+1}' for i in range(len(args.urls))]
        pdfs = [{'name': n, 'url': u} for n, u in zip(names, args.urls)]
    else:
        pdfs = DEFAULT_PDFS
    
    logger.info(f"Fetching {len(pdfs)} PDF(s)")
    success = sum(1 for p in pdfs if fetch_pdf(p['url'], p['name'], args.output_dir, args.text_dir, not args.no_text, logger))
    logger.info(f"Complete: {success}/{len(pdfs)} successful")
    return 0 if success == len(pdfs) else 1


if __name__ == '__main__':
    exit(main())
