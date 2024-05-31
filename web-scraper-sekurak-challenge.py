import requests, re
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

###
# Web Scraper for the Sekurak Hash Cracking challenge.
# It has the task of preparing data with certain parameters, which are to be further used to train the GTP-2 model. 
###

url = 'https://xyz.domain'		# url target
link_depth = 1 					# don't go too crazy here; max value: 2

def fetch_data(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        else:
            print(f"Failed to fetch {url}")
            return ""
    except Exception as err:
        print(f"Error fetching {url}: {str(err)}")
        return ""

def get_links(html, base_url):
    soup = BeautifulSoup(html, 'html.parser')
    links = set()
    for link in soup.find_all('a', href=True):
        href = link['href']
        full_url = urljoin(base_url, href)
        # filter out external links and keep only these links that belong to the base domain
        if urlparse(base_url).netloc == urlparse(full_url).netloc:
            links.add(full_url)
    return links

def normalize_text(text):
	# normalize text for the Sekurak Hash Crack challenge requirements:
	# - only sentences consisting of precisely 5 words, without Polish characters
    text = re.sub(r'[ąćęłńóśżź]', lambda x: {'ą':'a', 'ć':'c', 'ę':'e', 'ł':'l', 'ń':'n', 'ó':'o', 'ś':'s', 'ż':'z', 'ź':'z'}[x.group()], text)
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    text = text.lower()
    words = text.split()
    sentences = [' '.join(words[i:i+5]) for i in range(0, len(words), 5) if len(words[i:i+5]) == 5]
    return sentences

def main(url, depth=link_depth):
    visited = set()
    data = ""
    queue = [(url, 0)]

    while queue:
        current_url, current_depth = queue.pop(0)
        if current_url not in visited and current_depth <= depth:
            visited.add(current_url)
            html = fetch_data(current_url)
            if html:
                # add current pages text to the data
                soup = BeautifulSoup(html, 'html.parser')
                paragraphs = soup.find_all('p')
                text = ' '.join(p.get_text() for p in paragraphs)
                data += text + ' '
                
                # add only links if we are not at the last depth level
                if current_depth < depth:
                    links = get_links(html, current_url)
                    for link in links:
                        queue.append((link, current_depth + 1))
    
    return normalize_text(data)

if __name__ == "__main__":
	collected_data = main(url)

	print('\n'.join(collected_data[:10]))		# restrict output by number of lines 
	# print('\n'.join(collected_data))			# output


