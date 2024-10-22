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

# TODO: Move later. This will hold phrases that need to be excluded from criteria
#  
criteria_keys = ['note:','campus','any postgraduate', 'conditions', 'preference to', 'course offered', '2nd / 3rd', '1st/ 2nd', 'study mode']

def clean_criteria(given_points):
    filtered_critera = []
    for point in given_points:
        point = point.lower()
        if not any(phrase in point for phrase in criteria_keys):
            filtered_critera.append(point)

    for i in range(len(filtered_critera)):
        if "rural" in filtered_critera[i].lower() or "regional" in filtered_critera[i].lower():
            filtered_critera[i] = "Rural or Regional"
        elif "female" in filtered_critera[i].lower():
            filtered_critera[i] = "Female"
        if "academic performance" in filtered_critera[i].lower() or "sound academic record" in filtered_critera[i].lower() or "atar" in filtered_critera[i].lower():
            filtered_critera[i] = "Academic merit"
        
        if "financial hardship" in filtered_critera[i].lower():
            filtered_critera[i] = "Financial hardship"
        if "educational challenges" in filtered_critera[i].lower() or "equity scholarships" in filtered_critera[i].lower() or "equity application" in filtered_critera[i].lower():
            filtered_critera[i] = "Equity criteria"
        if "statement outlining" in filtered_critera[i].lower() or "attached as a word" in filtered_critera[i].lower():
            filtered_critera[i] = "Provide statement"
        if "disability" in filtered_critera[i].lower():
            filtered_critera[i] = "Disability" 
        if "answer the following" in filtered_critera[i].lower():
            filtered_critera[i] = "Provide a statement" 
        
    
    formatted_data = list(set(filtered_critera))
    return formatted_data

def CS_check_crit(given_soup):
    cond_ava = given_soup.find('strong', string=lambda text: text and "AVAILABLE TO:" in text)
    cond_must = given_soup.find('strong', string=lambda text: text and "MUST BE STUDYING IN:" in text)
    
    if cond_ava:
        condition = cond_ava
    else:
        condition = cond_must
    
    conditions_paragraphs = []
    if condition:
        siblings = condition.find_all_next()
        for sibling in siblings:
        # Stop if we hit another <div> or notes
            if sibling.name == 'div' or (sibling.name == 'strong' and "NOTE:" in sibling.get_text()):
                break
        
        # Collect <p> elements
            if sibling.name == 'p':
                conditions_paragraphs.append(sibling)
            if sibling.name == 'ul':
            # Get all <li> elements in this <ul>
                list_items = sibling.find_all('li')
                conditions_paragraphs.extend(list_items)
    
    cleaned_list = []
    for p in conditions_paragraphs:
        cleaned_list.append(p.get_text(strip=True))
    return cleaned_list


def search_page(page_url):
    response = requests.get(page_url)
    soup = BeautifulSoup(response.content, "html.parser")
    scholarship_name = soup.find('div', class_='container first').get_text(strip=True)
    
    has_indig = any(key in scholarship_name.lower() for key in indigenous_keys)
    if has_indig:
        return

    if "placement" in scholarship_name.lower() or "work integrated" in scholarship_name.lower():
        placem="Yes"

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
    
    # The pages have hidden html with unique (maybe) codes for each tab
    # Hence the need to use select and match with tab1_
    eligibility_div = soup.select('div[id^="tab1_"]')

    if eligibility_div:
        level = check_level(eligibility_div[0].get_text(strip=True))

    # TODO: this returns a list of all potential criteria. This now 
    # needs to be cleaned in clean_criteria
    criteria_list = CS_check_crit(soup)
    eligi_done = clean_criteria(criteria_list)
    # remove empties
    eligi_done = [elem for elem in eligi_done if elem]
    print(eligi_done)
    
   # print("Val:", value, "\nDuration:", duration, "\nLevel:", level)
# this one doesnt work
test_url = "https://www.csu.edu.au/scholarships/scholarships-grants/find-scholarship/equity/charles-sturt-kickstart-scholarship"
test_url2 = "https://www.csu.edu.au/scholarships/scholarships-grants/find-scholarship/foundation/any-year/vivability-limited-empowered-futures-scholarship"
test_pg = "https://www.csu.edu.au/scholarships/scholarships-grants/find-scholarship/foundation/continuing/online-study-student-representative-committee-post-graduate-scholarship"
search_page(test_pg)



# TODO: Main iteration

main_url = "https://www.csu.edu.au/scholarships?queries_status_query_posted=1&queries_status_query%5B0%5D=Commencing&queries_status_query%5B1%5D=Continuing&queries_type_query_posted=1&queries_type_query%5B0%5D=Internal&queries_levelofstudy_query_posted=1&queries_levelofstudy_query%5B0%5D=UG&queries_levelofstudy_query%5B1%5D=Hon&queries_levelofstudy_query%5B2%5D=PG&queries_faculty_query_posted=1&queries_faculty_query%5B0%5D=Arts+and+Education&queries_faculty_query%5B1%5D=Business%2C+Justice+%26+Behavioural+Sciences&queries_faculty_query%5B2%5D=Science&queries_studymode_query_posted=1&queries_studymode_query%5B0%5D=DE&queries_studymode_query%5B1%5D=OC&queries_studymode_query%5B2%5D=Mixed&queries_campus_query_posted=1&search_page_1218754_submit_button=Search"
soup_main = BeautifulSoup(main_url, 'html.parser')
#print(soup_main.find_all('a', href=True))

