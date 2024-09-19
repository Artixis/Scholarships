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
UNSW_data = []


def create_hyperlink(page_url, name):
    hyperlink = f'=HYPERLINK("{page_url}", "{name}")'
    return(hyperlink)

def type_check(equity_val):
    if equity_val:
        return "Equity"
    else:
        return "High Potential"

def concatenate_url(href_url):
    base_url = "https://www.scholarships.unsw.edu.au"
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
    UNSW_data.append(new_entry)

def search_page(page_URL):
    equity = False

    response = requests.get(page_URL)
    soup = BeautifulSoup(response.content, "html.parser")

    scholarship_name = soup.find('h1', class_='page-title').get_text(strip=True)

    scholarship_value = soup.find('div', class_='content').get_text(strip=True)
    scholarship_value = re.findall(value_pat, scholarship_value)

    scholarship_selection = soup.find('div', class_='section scholarships-selection')
    if scholarship_selection:
        scholarship_selection_text = scholarship_selection.get_text(strip=True).lower()
        for i in equity_keys:
            if(op.contains(scholarship_selection_text, i)):
                equity = True
                type_of_schol = type_check(equity)
    else:
        type_of_schol = "Null"

    scholarship_eligibility = soup.find('div', class_="section scholarships-eligibility")
    if scholarship_eligibility:
        list_items = scholarship_eligibility.find_all('li')
        if list_items:
            eligibility = [li.get_text(strip=True) for li in list_items]
        else:
            eligibility = [scholarship_eligibility.get_text(strip=True)]
    else:
        eligibility = "No Data Found"


    create_data_entry("UNSW", create_hyperlink(page_URL, scholarship_name), type_check(equity), scholarship_value, check_level(eligibility), eligibility)


main_URL = "https://www.scholarships.unsw.edu.au/scholarships/search?exclude=I&show=all"
main_page = requests.get(main_URL)
soup2 = BeautifulSoup(main_page.content, "html.parser")

# for UNSW 1-92
for i in range(1, 92):  
    div_class = f'row-content-{i} row-content col-1 clearfix'
    div = soup2.find('div', class_=div_class)
    a_tag = div.find('a')
    href_value = a_tag['href']

    url_i = concatenate_url(href_value)
    search_page(url_i)



df = pd.DataFrame(UNSW_data)
df.to_excel("scraped_UNSW_data.xlsx", index=False)
