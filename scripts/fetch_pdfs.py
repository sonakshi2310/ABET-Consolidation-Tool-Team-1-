"""Fetch PDFs from URLs - Simple PDF Scraper

QUICK START:
    # Fetch default PDFs (CS and CSE criteria)
    python scripts/fetch_pdfs.py

    # Fetch specific URLs
    python scripts/fetch_pdfs.py --urls https://example.com/file1.pdf https://example.com/file2.pdf

    # Custom output directory
    python scripts/fetch_pdfs.py --output-dir my_pdfs/

    # Skip text extraction (only download PDFs)
    python scripts/fetch_pdfs.py --no-text

USAGE:
    This script downloads PDFs from URLs and optionally extracts text.
    PDFs are saved to data/abet_pdfs/ by default.
    Text is saved to data/abet_pdf_text/ by default.

SCHEDULING:
    Use scripts/schedule_pdfs.py to set up automatic scheduling, or use cron/systemd.
    Example cron (runs 1st of every month at 9 AM):
        0 9 1 * * cd /path/to/project && python scripts/fetch_pdfs.py
"""
import os
import sys
import argparse
import logging
from datetime import datetime

# Add repo root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.abet_pdf_simple import get_pdf_from_url, read_pdf_text


# Default PDFs to fetch
DEFAULT_PDFS = [
    {
        "name": "CS_Criteria",
        "url": "https://www.abet.org/wp-content/uploads/2023/05/2024-2025_CAC_Criteria.pdf",
    },
    {
        "name": "CSE_Criteria",
        "url": "https://www.abet.org/wp-content/uploads/2023/05/2024-2025_EAC_Criteria.pdf",
    }
]


def setup_logging():
    """Setup simple logging."""
    os.makedirs('logs', exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/fetch_pdfs.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)


def save_file(content: bytes, filepath: str):
    """Save bytes to file."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'wb') as f:
        f.write(content)


def save_text(text: str, filepath: str):
    """Save text to file."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(text)


def fetch_pdf(url: str, name: str, pdf_dir: str, text_dir: str, extract_text: bool, logger: logging.Logger) -> bool:
    """Fetch a single PDF and save it.
    
    Returns:
        True if successful, False otherwise
    """
    try:
        logger.info(f"Fetching {name} from {url}")
        
        # Download PDF
        pdf_bytes = get_pdf_from_url(url)
        logger.info(f"Downloaded {name}: {len(pdf_bytes)} bytes")
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        pdf_filename = f"{name}_{timestamp}.pdf"
        text_filename = f"{name}_{timestamp}.txt"
        
        # Save PDF
        pdf_path = os.path.join(pdf_dir, pdf_filename)
        save_file(pdf_bytes, pdf_path)
        logger.info(f"Saved PDF: {pdf_path}")
        
        # Extract and save text if requested
        if extract_text:
            text = read_pdf_text(pdf_bytes)
            text_path = os.path.join(text_dir, text_filename)
            save_text(text, text_path)
            logger.info(f"Saved text: {text_path} ({len(text)} characters)")
        
        return True
        
    except Exception as e:
        logger.error(f"Error fetching {name}: {e}", exc_info=True)
        return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Fetch PDFs from URLs',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('--urls', nargs='+', help='PDF URLs to fetch', default=None)
    parser.add_argument('--names', nargs='+', help='Names for PDFs (same order as URLs)', default=None)
    parser.add_argument('--output-dir', help='Directory to save PDFs', default='data/abet_pdfs')
    parser.add_argument('--text-dir', help='Directory to save extracted text', default='data/abet_pdf_text')
    parser.add_argument('--no-text', action='store_true', help='Skip text extraction')
    args = parser.parse_args()
    
    # Setup logging
    logger = setup_logging()
    
    logger.info("=" * 60)
    logger.info("Starting PDF fetch")
    logger.info("=" * 60)
    
    # Determine PDFs to fetch
    if args.urls:
        # Use URLs from command line
        names = args.names if args.names else [f'PDF_{i+1}' for i in range(len(args.urls))]
        if len(names) != len(args.urls):
            logger.error("Number of names must match number of URLs")
            return 1
        pdfs = [{'name': name, 'url': url} for name, url in zip(names, args.urls)]
    else:
        # Use default PDFs
        pdfs = DEFAULT_PDFS
        logger.info("Using default PDFs (CS and CSE criteria)")
    
    if not pdfs:
        logger.error("No PDFs to fetch")
        return 1
    
    logger.info(f"Fetching {len(pdfs)} PDF(s)")
    
    # Fetch each PDF
    success_count = 0
    fail_count = 0
    
    for pdf in pdfs:
        if fetch_pdf(
            pdf['url'],
            pdf['name'],
            args.output_dir,
            args.text_dir,
            not args.no_text,
            logger
        ):
            success_count += 1
        else:
            fail_count += 1
    
    # Summary
    logger.info("=" * 60)
    logger.info(f"Complete: {success_count} successful, {fail_count} failed")
    logger.info("=" * 60)
    
    return 0 if fail_count == 0 else 1


if __name__ == '__main__':
    exit(main())

