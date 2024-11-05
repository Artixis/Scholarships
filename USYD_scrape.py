import requests
import re
import pickle
from bs4 import BeautifulSoup

value_pat = r'\$\d{1,3}(?:,\d{3})*'
year_pat = r'(\d+)\s+(?=years?|year)'
equity_keys = ['uac', 'equity', 'ES']
PG_keys = ['pg', 'master', 'postgraduate', 'masters']
UG_keys = ['ug', 'bachelor', 'undergraduate']
other_keys = ['phd', 'diploma', 'doctorate', 'honours']

data_raw = []

def create_hyperlink(page_url, name):
    hyperlink = f'=HYPERLINK("{page_url}", "{name}")'
    return(hyperlink)

def format_criteria(criteria_list):
    return '\n'.join([f'• {criteria}' for criteria in criteria_list])

def check_level(given_text):
    if isinstance(given_text, list):
        given_text = " ".join(given_text)

    given_text = given_text.lower()
    has_pg = any(key in given_text for key in PG_keys)
    has_ug = any(key in given_text for key in UG_keys)
    has_other = any(key in given_text for key in other_keys)

    if has_pg and has_ug:
        return "UG/PG"
    elif has_pg:
        return "PG"
    elif has_ug:
        return "UG"
    elif has_other:
        return "Other"
    else:
        return "Undefined"

def create_data_entry(name, url, type_of, value, level, criteria, duration="NA", indigenous="No", placement="No"):
    new_entry = {'University': name,
                 'Name': url,
                 'Type': type_of,
                 'Value': value,
                 'Duration': duration,
                 'Level': level,
                 'Criteria': criteria,
                 'Indigenous': indigenous,
                 'Placement': placement}
    data_raw.append(new_entry)

def find_value(given_info):
    scholarship_value = re.findall(value_pat, given_info.find('td').get_text(strip=True))
    if scholarship_value:
        scholarship_value = scholarship_value[0]
    return scholarship_value

def check_duration(value_info):
    if "duration" in value_info.lower():
        duration = "Duration of degree"
    elif "one off" in value_info.lower():
        duration = "One-off"
    elif "year" in value_info.lower():
        year_num = re.search(year_pat, value_info.lower())
        duration = f"{year_num.group(1)} years"
    else:
        duration = "na"
    return duration


word_to_num = {
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10
}

# TODO: fix the ordering of this code. messy

def get_duration(tnc_soup):
    value_section = tnc_soup.find_all(string="4. Value")[0].find_next('p')
    if not value_section.get_text(strip=True):
        value_section = value_section.find_next('p', string=lambda text: text and text.strip())
    print(value_section)
    
    duration_text = value_section.get_text()
    
    if "determined by the Dean" in duration_text or "determined by the Head of School" in duration_text:
        return ("Determined by Dean")
    
    if "duration of the" in duration_text:
        return ("Duration of Degree")
    
    match = re.search(r'(\d+|\b(?:one|two|three|four|five|six|seven|eight|nine|ten)\b)\s*year(s)?', duration_text)
    if match:
        duration_years = match.group(1)
        if duration_years.isdigit():
            duration_years = int(duration_years)
        else:
            duration_years = word_to_num[duration_years]
    
    duration = f"{duration_years} years"
    
    return(duration)

def search_page(page_url):
    equity = False
    indigen = "No"
    type_of_schol = "NULL"

    response = requests.get(page_url)
    soup = BeautifulSoup(response.content, "html.parser")
    title_tag = soup.find('title')
    if title_tag and "404 resource" in title_tag.string.lower():
        return

    scholarship_name = soup.find('h1', class_='pageTitle').get_text(strip=True)
    if "travel" in scholarship_name.lower():
        return
    scholarship_info = soup.find('div', class_='richTextModule b-single-column__container')

    val = find_value(scholarship_info)

    terms_and_conds = soup.find('div', class_='content richTextModule')
    duration = get_duration(terms_and_conds)

    eligibility_items = scholarship_info.findAll('li')
    if eligibility_items:
        eligibility = [li.get_text(strip=True) for li in eligibility_items]
        contains_indi = any("indigenous" in li.get_text(strip=True).lower() for li in eligibility_items)
        if contains_indi:
            indigen = "Preference"
    
    summary_text = soup.find('div', class_='cq-editable-inline-text').get_text(strip=True)
    #print(summary_text)
    create_data_entry("USYD", create_hyperlink(page_url, scholarship_name), type_of_schol, val, check_level(summary_text), eligibility, duration = duration, indigenous = indigen)


with open('my_urls.pkl', 'rb') as file:
    url_list = pickle.load(file)
url_list = sorted(url_list)

test_num = 0

for url in url_list:
    if test_num < 360:
        print("**\Test Num: ", test_num, "\n**")
        print(url)
        search_page(url)
    test_num += 1

