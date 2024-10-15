import requests
import re
import pandas as pd
from word2number import w2n
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

indigenous_keys = ['indigenous', 'ATSI', 'aboriginal']
data_raw = []

def check_duration(value_info):
    duration = "na"
    if "duration" in value_info.lower():
        duration = "Duration of degree"
    elif "one off" in value_info.lower():
        duration = "One-off"
    elif "instalments" in value_info.lower():
        duration ="1 years"
    elif "year" in value_info.lower() or "years" in value_info.lower():
        year_num = re.search(r'(\d+)', value_info.lower())
        duration = f"{year_num.group(1)} years"
    else:
        duration = "na"
    return duration



def search_page(page_url):
    response = requests.get(page_url)
    soup = BeautifulSoup(response.content, "html.parser")
    scholarship_name = soup.find('div', class_='container first').get_text(strip=True)
    
    schol_details = soup.find('div', class_='col-wrap-1a w-col-4')
    strong_elements = schol_details.find_all('strong')
    for strong in strong_elements:
        key = strong.get_text(strip=True)
        #print(key)
        if "Value" in key:
            value = strong.next_sibling.strip()
        if "Duration" in key:
            dur_text = strong.next_sibling.strip()
            duration = check_duration(dur_text)
    print("Val:", value, "\nDuration:", duration)

test_url = "https://www.csu.edu.au/scholarships/scholarships-grants/find-scholarship/equity/charles-sturt-kickstart-scholarship#tab1"
search_page(test_url)

'''
For the level of study, there's a few options 

MUST BE STUDYING IN:

STUDENTS STUDYING IN:

Or we would need to check the CONDITIONS: and match keys
'''
main_url = "https://www.csu.edu.au/scholarships?queries_status_query_posted=1&queries_status_query%5B0%5D=Commencing&queries_status_query%5B1%5D=Continuing&queries_type_query_posted=1&queries_type_query%5B0%5D=Internal&queries_levelofstudy_query_posted=1&queries_levelofstudy_query%5B0%5D=UG&queries_levelofstudy_query%5B1%5D=Hon&queries_levelofstudy_query%5B2%5D=PG&queries_faculty_query_posted=1&queries_faculty_query%5B0%5D=Arts+and+Education&queries_faculty_query%5B1%5D=Business%2C+Justice+%26+Behavioural+Sciences&queries_faculty_query%5B2%5D=Science&queries_studymode_query_posted=1&queries_studymode_query%5B0%5D=DE&queries_studymode_query%5B1%5D=OC&queries_studymode_query%5B2%5D=Mixed&queries_campus_query_posted=1&search_page_1218754_submit_button=Search"
soup_main = BeautifulSoup(main_url, 'html.parser')
links = [a['href'] for a in soup_main.find_all('a', href=True)]

# Print the links
for link in links:
    print(link)