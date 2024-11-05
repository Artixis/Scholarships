import requests
import pickle
from bs4 import BeautifulSoup

# TODO: Can use concat function to shorten this
pages_to_scrape = ['https://www.sydney.edu.au/scholarships/domestic/bachelors-honours/general.html', 'https://www.sydney.edu.au/scholarships/domestic/bachelors-honours/faculty/architecture.html', 'https://www.sydney.edu.au/scholarships/domestic/bachelors-honours/faculty/arts-social-sciences.html',
                   'https://www.sydney.edu.au/scholarships/domestic/bachelors-honours/faculty/business.html', 'https://www.sydney.edu.au/scholarships/domestic/bachelors-honours/faculty/engineering.html',
                   'https://www.sydney.edu.au/scholarships/domestic/bachelors-honours/faculty/law.html', 'https://www.sydney.edu.au/scholarships/domestic/bachelors-honours/faculty/medicine-health.html',
                   'https://www.sydney.edu.au/content/corporate/scholarships/domestic/bachelors-honours/faculty/music.html', 'https://www.sydney.edu.au/scholarships/domestic/bachelors-honours/faculty/science.html',
                   'https://www.sydney.edu.au/scholarships/domestic/bachelors-honours/equity.html', 'https://www.sydney.edu.au/scholarships/domestic/postgraduate-coursework/general.html',
                   'https://www.sydney.edu.au/scholarships/domestic/postgraduate-coursework/faculty/architecture.html', 'https://www.sydney.edu.au/scholarships/domestic/postgraduate-coursework/faculty/arts-social-sciences.html',
                   'https://www.sydney.edu.au/scholarships/domestic/postgraduate-coursework/faculty/business.html', 'https://www.sydney.edu.au/scholarships/domestic/postgraduate-coursework/faculty/engineering.html',
                   'https://www.sydney.edu.au/scholarships/domestic/postgraduate-coursework/faculty/law.html', 'https://www.sydney.edu.au/scholarships/domestic/postgraduate-coursework/faculty/medicine-health.html',
                   'https://www.sydney.edu.au/scholarships/domestic/postgraduate-coursework/faculty/music.html', 'https://www.sydney.edu.au/scholarships/domestic/postgraduate-coursework/faculty/science.html']

print(len(pages_to_scrape))

urls = set() 

def concatenate_url(base_url, href_url):
    return f"{base_url}{href_url}"


def collect_URLS(url_curr):
    response = requests.get(url_curr)
    soup_general = BeautifulSoup(response.content, 'html.parser')
    main_section = soup_general.find('div', class_='bodyColumn')
    for a in main_section.find_all('a', href=True):
        href = a['href']
        if href.startswith('/content/corporate/') and href not in urls:
            urls.add(concatenate_url("https://www.sydney.edu.au/scholarships/", href.replace('/content/corporate/scholarships/', '')))
    return

for i in range(len(pages_to_scrape)):
    collect_URLS(pages_to_scrape[i])

print(len(urls))

with open('my_urls.pkl', 'wb') as file:
    pickle.dump(urls, file)
