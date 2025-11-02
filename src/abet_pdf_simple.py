"""Simple ABET PDF scraper - just download and extract text.
Usage:
    Option 1: In Python code
        from src.abet_pdf_simple import scrape_pdf
        
        text = scrape_pdf('https://www.abet.org/.../criteria.pdf')
        print(text)
    
    Option 2: Command line
        python src/abet_pdf_simple.py https://example.com/document.pdf
        python src/abet_pdf_simple.py https://example.com/document.pdf -o output.txt
    
    Option 3: Step by step
        from src.abet_pdf_simple import get_pdf_from_url, read_pdf_text
        
        pdf_bytes = get_pdf_from_url('https://example.com/document.pdf')
        text = read_pdf_text(pdf_bytes)

Requirements:
    pip install pypdf requests
    pip install beautifulsoup4
"""
import requests
import io
from urllib.parse import urljoin

try:
    from pypdf import PdfReader
except ImportError:
    try:
        import PyPDF2
        PdfReader = PyPDF2.PdfReader
    except ImportError:
        PdfReader = None

try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None


def get_pdf_from_url(url: str, timeout: int = 30) -> bytes:
    """Download a PDF from a URL.
    
    Args:
        url: URL of the PDF
        timeout: Request timeout in seconds
        
    Returns:
        PDF content as bytes
        
    Raises:
        requests.RequestException on network errors
    """
    resp = requests.get(url, timeout=timeout, allow_redirects=True)
    resp.raise_for_status()
    return resp.content


def read_pdf_text(pdf_bytes: bytes) -> str:
    """Extract all text from a PDF.
    
    Args:
        pdf_bytes: PDF content as bytes
        
    Returns:
        Extracted text as a single string
        
    Raises:
        ImportError if PDF library not installed
    """
    if PdfReader is None:
        raise ImportError(
            "PDF library required. Install with: pip install pypdf"
        )
    
    pdf_file = io.BytesIO(pdf_bytes)
    reader = PdfReader(pdf_file)
    
    text_parts = []
    for page in reader.pages:
        text = page.extract_text()
        text_parts.append(text)
    
    return '\n'.join(text_parts)


def scrape_pdf(url: str) -> str:
    """Download PDF from URL and extract text.
    
    Args:
        url: URL of PDF to download
        
    Returns:
        Extracted text
        
    Example:
        text = scrape_pdf('https://example.com/document.pdf')
    """
    pdf_bytes = get_pdf_from_url(url)
    text = read_pdf_text(pdf_bytes)
    return text


def find_pdf_url_on_page(page_url: str, link_text: str = 'Download the Criteria') -> str:
    """Find PDF download link on a webpage.
    
    Args:
        page_url: URL of the webpage containing the PDF link
        link_text: Text to search for in the link (default: 'Download the Criteria')
        
    Returns:
        Full URL to the PDF
        
    Raises:
        ImportError if BeautifulSoup not installed
        ValueError if PDF link not found
    """
    if BeautifulSoup is None:
        raise ImportError(
            "BeautifulSoup required. Install with: pip install beautifulsoup4"
        )
    
    # Get the webpage
    response = requests.get(page_url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Try to find the specific download link
    download_link = soup.find('a', string=lambda text: text and link_text in text)
    
    if download_link and download_link.get('href'):
        pdf_url = urljoin(page_url, download_link['href'])
        return pdf_url
    
    # Fallback: try to find any link with 'button' class (like in your original code)
    button_link = soup.find('a', class_='button')
    if button_link and button_link.get('href'):
        pdf_url = urljoin(page_url, button_link['href'])
        return pdf_url
    
    raise ValueError(f"Could not find PDF download link on page: {page_url}")


def scrape_pdf_from_page(page_url: str, link_text: str = 'Download the Criteria', 
                          save_pdf: str = None) -> str:
    """Find and download PDF from a webpage, then extract text.
    
    Args:
        page_url: URL of webpage containing PDF link
        link_text: Text to search for in the link
        save_pdf: Optional filename to save the PDF locally
        
    Returns:
        Extracted text from PDF
        
    Example:
        text = scrape_pdf_from_page(
            'https://www.abet.org/accreditation/accreditation-criteria/criteria-for-accrediting-computing-programs-2025-2026/'
        )
    """
    # Find the PDF URL
    print(f"Searching for PDF link on {page_url}...")
    pdf_url = find_pdf_url_on_page(page_url, link_text)
    print(f"Found PDF: {pdf_url}")
    
    # Download the PDF
    print("Downloading PDF...")
    pdf_bytes = get_pdf_from_url(pdf_url)
    
    # Optionally save the PDF
    if save_pdf:
        with open(save_pdf, 'wb') as f:
            f.write(pdf_bytes)
        print(f"PDF saved to {save_pdf}")
    
    # Extract text
    print("Extracting text...")
    text = read_pdf_text(pdf_bytes)
    
    return text


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Download and extract text from a PDF')
    parser.add_argument('url', help='PDF URL or webpage URL')
    parser.add_argument('--output', '-o', help='Output text file (optional)', default=None)
    parser.add_argument('--save-pdf', '-p', help='Save PDF file (optional)', default=None)
    parser.add_argument('--from-page', '-f', action='store_true', 
                       help='URL is a webpage, not direct PDF link')
    args = parser.parse_args()
    
    try:
        if args.from_page:
            print(f"Scraping PDF from webpage: {args.url}...")
            text = scrape_pdf_from_page(args.url, save_pdf=args.save_pdf)
        else:
            print(f"Downloading PDF from {args.url}...")
            text = scrape_pdf(args.url)
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(text)
            print(f"Text saved to {args.output}")
        else:
            print("\nExtracted text:")
            print(text[:500] + "..." if len(text) > 500 else text)
            
    except Exception as e:
        print(f"Error: {e}")
        exit(1)


'''
To run this code navigate to the src file and run the following commands in the terminal:

For Computing/CS programs:
python abet_pdf_simple.py "https://www.abet.org/accreditation/accreditation-criteria/criteria-for-accrediting-computing-programs-2025-2026/" --from-page -o cs_criteria.txt

For Engineering programs:
python abet_pdf_simple.py "https://www.abet.org/accreditation/accreditation-criteria/criteria-for-accrediting-engineering-programs-2025-2026/" --from-page -o eac_criteria.txt
'''