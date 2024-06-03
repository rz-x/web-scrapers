import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin, urlparse
import time

###
# Multi-page sentences scraper with in-code-parameters.
###

scrape_urls = [
    'https://xyz-1.com',
    'https://xyz-2.com',
    'https://xyz-X.com'
]  

max_depth = 2   # don't go too crazy here; max value: 2
delay = 0.2

# Mode options for the sentence lenght: 'no_restriction', 'range', 'exact' 
mode = 'no_restriction'
# mode = 'exact'
# mode = 'range'

min_len = 4
max_len = 7
exact_len = 0

def extract_urls(soup, base_url):
    urls = []
    for a in soup.find_all('a', href=True):
        full_url = urljoin(base_url, a['href'])
        urls.append(full_url)
    return urls

def fetch_html(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        if response.headers['Content-Type'].lower().startswith('text/html'):
            return response.text
    except requests.RequestException as err:
        print(f"Error fetching {url}: {err}")
    return None

def extract_sentences(html, mode='no_restriction', min_len=0, max_len=0, exact_len=0):
    soup = BeautifulSoup(html, 'html.parser')
    text = soup.get_text()
    sentences = []
    if mode == 'no_restriction':
        sentences = re.findall(r'\b[A-Z][a-z]*\b(?: \b[a-z]+\b)+\.', text)
    elif mode == 'range':
        pattern = r'\b[A-Z][a-z]*\b(?: \b[a-z]+\b){' + str(min_len - 1) + ',' + str(max_len - 1) + r'}\.'
        sentences = re.findall(pattern, text)
    elif mode == 'exact':
        pattern = r'\b[A-Z][a-z]*\b(?: \b[a-z]+\b){' + str(exact_len - 1) + r'}\.'
        sentences = re.findall(pattern, text)
    return sentences

def go_scrape(scrape_urls, max_depth, delay, mode, min_len=0, max_len=0, exact_len=0):
    visited = set()
    to_visit = [(url, 0) for url in scrape_urls]
    sentences = []

    while to_visit:
        url, depth = to_visit.pop(0)
        if depth > max_depth or url in visited:
            continue
        visited.add(url)

        html = fetch_html(url)
        if html:
            new_sentences = extract_sentences(html, mode, min_len, max_len, exact_len)
            for sentence in new_sentences:
                print(sentence)
                sentences.append(sentence)

            if depth < max_depth:
                soup = BeautifulSoup(html, 'html.parser')
                new_urls = extract_urls(soup, url)
                to_visit.extend((new_url, depth + 1) for new_url in new_urls if urlparse(new_url).netloc == urlparse(url).netloc)

        time.sleep(delay)

    return sentences

if __name__ == '__main__':
    go_scrape(scrape_urls, max_depth, delay, mode, min_len, max_len, exact_len)

