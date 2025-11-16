#install:
#pip install pypdf requests
#pip install beautifulsoup4

import requests
import io
#import os
#import sys
import difflib
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from pypdf import PdfReader
import PyPDF2

#gets the pdf from the url
def get_pdf_from_url(url: str, timeout: int = 30) -> bytes:

    resp = requests.get(url, timeout=timeout, allow_redirects=True)
    resp.raise_for_status()
    return resp.content

#parses through pdf and saves the text into a list
def read_pdf_text(pdf_bytes: bytes) -> str:

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



#this function scrapes the pdf link from the page and returns the link as a string
def find_pdf_url_on_page(page_url: str, link_text: str = 'Download the criteria') -> str:


    
    #scrapes the webpage
    response = requests.get(page_url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    print("FDHSKJFLDS")


    #dont think this is needed?
    #download_link = soup.find('a', string=lambda text: text and link_text in text)
    #print(download_link)
    #if download_link and download_link.get('href'):
    #    pdf_url = urljoin(page_url, download_link['href'])
    #    return pdf_url
    
    getlink = 'Download the Criteria'
    #scrapes link from the website

    #pdf links are different from cs and cse in the html structure so this checks for href, getting all lowercase for string lambda bypasses weird navigation thing
    button_link = soup.find("a", href=True, string=lambda s: s and getlink.lower() in s.lower())

    #gets cs link
    #soup.find('a', class_='button')
    print(button_link)
    #button_link = soup.find('a', string= link_text)
   
    if button_link and button_link.get('href'):
        pdf_url = urljoin(page_url, button_link['href'])
        
       
        return pdf_url
    
    raise ValueError(f"Could not find PDF download link on page: {page_url}")

#this function scrapes the pdf from the ABET page and extracts the text and returns it as a string
def scrape_pdf_from_page(page_url: str, link_text: str = 'Download the Criteria', 
                          save_pdf: str = None) -> str:

    # Find the PDF URL
    print(f"Searching for PDF link onn {page_url}")
    pdf_url = find_pdf_url_on_page(page_url, link_text)
    print(f"Found PDF: {pdf_url}")
    
    # Download the PDF
    print("Downloading PDF")
    pdf_bytes = get_pdf_from_url(pdf_url)
    
    #save the PDF
    if save_pdf:
        with open(save_pdf, 'wb') as f:
            f.write(pdf_bytes)
        print(f"PDF saved to {save_pdf}")
    
    # Extract text
    print("getting text")
    text = read_pdf_text(pdf_bytes)
    
    return text

#not needed? since already being used in email code?
#min diff function for comparing two txt files and showing the changes
"""def mindiff_text_files(path_a: str, path_b: str, out_path: str = None, context: int = 3) -> str:

    if not os.path.exists(path_a):
        raise ValueError(f'File not found: {path_a}')
    if not os.path.exists(path_b):
        raise ValueError(f'File not found: {path_b}')

    with open(path_a, 'r', encoding='utf-8', errors='replace') as fa:
        a_lines = fa.read().splitlines()
    with open(path_b, 'r', encoding='utf-8', errors='replace') as fb:
        b_lines = fb.read().splitlines()

    if out_path is None:
        a_base = os.path.splitext(os.path.basename(path_a))[0]
        b_base = os.path.splitext(os.path.basename(path_b))[0]
        out_name = f"{a_base}+{b_base}_diff.txt"
        out_path = os.path.join(os.path.dirname(path_a) or '.', out_name)

    diff_lines = list(difflib.unified_diff(a_lines, b_lines,
                                           fromfile=path_a,
                                           tofile=path_b,
                                           n=context,
                                           lineterm=''))

    with open(out_path, 'w', encoding='utf-8') as out_f:
        if not diff_lines:
            out_f.write('')
        else:
            out_f.write('\n'.join(diff_lines))

    return out_path
"""

if __name__ == '__main__':


    CS_url = "https://www.abet.org/accreditation/accreditation-criteria/criteria-for-accrediting-computing-programs-2025-2026/"
    CS_text = "cs_criteria.txt"
    CSE_url = "https://www.abet.org/accreditation/accreditation-criteria/criteria-for-accrediting-engineering-programs-2025-2026/"
    CSE_text = "cse_criteria.txt"
    save_pdf = ""


    #scrape cs pdf into txt file
    print(f"Scraping PDF from webpage: {CS_url}")
    text = scrape_pdf_from_page(CS_url, save_pdf)

    with open(CS_text, 'w', encoding='utf-8') as f:
        f.write(text)
    print(f"Text saved to {CS_text}")



    #scrape cse pdf into txt file
    print(f"Scraping PDF from webpage: {CSE_url}")
    text = scrape_pdf_from_page(CSE_url, save_pdf)

    with open(CSE_text, 'w', encoding='utf-8') as f:
        f.write(text)
    print(f"Text saved to {CS_text}")
   



