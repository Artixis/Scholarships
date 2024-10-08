import requests
import re
import pandas as pd
import operator as op
from bs4 import BeautifulSoup
import openpyxl
from openpyxl.styles import Font

value_pat = r'\$\d{1,3}(?:,\d{3})*'
equity_keys = ['uac', 'equity', 'ES']
PG_keys = ['pg', 'master', 'postgraduate', 'masters']
UG_keys = ['ug', 'bachelor', 'undergraduate']
other_keys = ['phd', 'diploma', 'doctorate', 'honours']

data_raw = []

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

def create_data_entry(name, url, type_of, value, level, conditions):
    new_entry = {'University': name,
                 'Name': url,
                 'Type': type_of,
                 'Value': value,
                 'Level': level,
                 'Conditions': conditions}
    data_raw.append(new_entry)


def search_page(page_url):

    response = requests.get(page_url)
    soup = BeautifulSoup(response.content, "html.parser")

    scholarship_name = soup.find('h1', class_='pageTitle').get_text(strip=True)
    scholarship_value_info = soup.find('div', class_='richTextModule b-single-column__container')
    #print(scholarship_value_info)
    scholarship_value = re.findall(value_pat, scholarship_value_info.find('td').get_text(strip=True)) 
    print(scholarship_value[0])


test_url = "https://www.sydney.edu.au/scholarships/e/adam-scott-foundation-scholarship.html"

search_page(test_url)




