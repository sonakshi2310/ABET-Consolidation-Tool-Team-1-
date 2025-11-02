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
"""
import requests
import io

try:
    from pypdf import PdfReader
except ImportError:
    try:
        import PyPDF2
        PdfReader = PyPDF2.PdfReader
    except ImportError:
        PdfReader = None


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
    resp = requests.get(url, timeout=timeout)
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


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Download and extract text from a PDF')
    parser.add_argument('url', help='PDF URL')
    parser.add_argument('--output', '-o', help='Output text file (optional)', default=None)
    args = parser.parse_args()
    
    try:
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
"""
#ill probably integrate this part later
import requests
from bs4 import BeautifulSoup
import numpy

#getting CS ABET url here
CS_url = 'https://www.abet.org/accreditation/accreditation-criteria/criteria-for-accrediting-computing-programs-2025-2026/'

CS_page = requests.get(CS_url)

CS_soup = BeautifulSoup(CS_page.text, 'html')

#grabbing pdf area
CS_stud_outcome = CS_soup.find('a', class_ = 'button')
print(CS_stud_outcome)


#getting pdf part from the scraped <a class... part
PDFpart = CS_stud_outcome["href"]
print(PDFpart)

#PDF: https://www.abet.org/2025-2026_cac_criteria/


"""
