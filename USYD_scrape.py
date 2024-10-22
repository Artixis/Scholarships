'''
PULL FIRST YA SILLY
'''
import requests
import re
import pandas as pd
import operator as op
from bs4 import BeautifulSoup
import openpyxl
from openpyxl.styles import Font

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

def concatenate_url(base_url, href_url):
    return f"{base_url}{href_url}"

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

def search_page(base_url, page_url):

    url = concatenate_url(base_url, page_url)
    equity = False
    indigen = "No"
    type_of_schol = "NULL"

    response = requests.get(page_url)
    soup = BeautifulSoup(response.content, "html.parser")

    scholarship_name = soup.find('h1', class_='pageTitle').get_text(strip=True)
    if "travel" in scholarship_name.lower():
        return
    scholarship_info = soup.find('div', class_='richTextModule b-single-column__container')

    val = find_value(scholarship_info)

    duration = check_duration(scholarship_info.find('td').get_text(strip=True))

    eligibility_items = scholarship_info.findAll('li')
    if eligibility_items:
        eligibility = [li.get_text(strip=True) for li in eligibility_items]
        contains_indi = any("indigenous" in li.get_text(strip=True).lower() for li in eligibility_items)
        if contains_indi:
            indigen = "Preference"
    
    summary_text = soup.find('div', class_='cq-editable-inline-text').get_text(strip=True)
    print(summary_text)
    create_data_entry("USYD", create_hyperlink(page_url, scholarship_name), type_of_schol, val, check_level(summary_text), eligibility, duration = duration, indigenous = indigen)


test_url = "https://www.sydney.edu.au/scholarships/e/adam-scott-foundation-scholarship.html"

#search_page("", test_url)
#print(data_raw)

year_num = re.search('\b(\d+)\b|\((\d+)\)', "1 year")
print(year_num)
duration = f"{year_num.group(1)} years"