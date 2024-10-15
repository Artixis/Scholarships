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
criteria_keys =['application via uow', 'any uow coursework', 'eligible for enrolment', 'must be commencing study', 'statement demonstrating', 'meet all entry requirements', 'engage with', 'scholarship cannot be deferred', 'must remain enrolled', 'must maintain a minimum', 'requested to interact', 'australian citizen']
indigenous_keys = ['indigenous', 'ATSI', 'aboriginal']
data_raw = []

def create_hyperlink(page_url, name):
    hyperlink = f'=HYPERLINK("{page_url}", "{name}")'
    return(hyperlink)

def format_criteria(criteria_list):
    return '\n'.join([f'• {criteria}' for criteria in criteria_list])

def concatenate_url(base_url, href_url):
    return f"{base_url}{href_url}"

def create_data_entry(url, type_of, value, level, criteria, duration="NA", indigenous="No", placement="No"):
    new_entry = {'University': "UOW",
                 'Name': url,
                 'Type': type_of,
                 'Value': value,
                 'Duration': duration,
                 'Level': level,
                 'Criteria': criteria,
                 'Indigenous': indigenous,
                 'Placement': placement}
    data_raw.append(new_entry)

# TODO: Find more examples DOD may not be correct in this example
def check_duration(value_info):
    duration = "na"
    if "duration" in value_info.lower():
        duration = "Duration of degree"
    elif "one off" in value_info.lower():
        duration = "One-off"
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

def clean_criteria(given_points):
    filtered_critera = []
    for point in given_points:
        point = point.lower()
        if not any(phrase in point for phrase in criteria_keys):
            filtered_critera.append(point)

    for i in range(len(filtered_critera)):
        if "rural" in filtered_critera[i].lower():
            filtered_critera[i] = "Rural or Regional"
        if "female candidates" in filtered_critera[i].lower():
            filtered_critera[i] = "Female Preference"
        elif "female" in filtered_critera[i].lower():
            filtered_critera[i] = "Female"
        if "demonstrated excellence" in filtered_critera[i].lower() or "maintained a grade" in filtered_critera[i].lower() or "atar" in filtered_critera[i].lower():
            filtered_critera[i] = "Academic merit"
        
        if "social housing" in filtered_critera[i].lower():
            filtered_critera[i] = "Financial hardship"
        if "educational challenges" in filtered_critera[i].lower() or "equity scholarships" in filtered_critera[i].lower() or "equity application" in filtered_critera[i].lower():
            filtered_critera[i] = "Equity criteria"
        if "statement outlining" in filtered_critera[i].lower():
            filtered_critera[i] = "Provide statement"
    
    formatted_data = list(set(filtered_critera))
    return formatted_data


def search_page(page_url):

    placem="No"

    response = requests.get(page_url)
    soup = BeautifulSoup(response.content, "html.parser")
    scholarship_name = soup.find('div', class_='grid_12 box').get_text(strip=True)

    has_indig = any(key in scholarship_name.lower() for key in indigenous_keys)
    if has_indig:
        return

    if "placement" in scholarship_name.lower() or "work integrated" in scholarship_name.lower():
        placem="Yes"

    for row in soup.select('table.table tr'):
        strong_text = row.find('strong')
        if strong_text:
            if "Value" in strong_text:
                value = (row).find('td').text.split()[1]
            if "Duration" in strong_text:

                words = (row).find('td').text.split()
                sentence = ' '.join(words[1:])
                duration = check_duration(sentence)

            if "Graduate Type" in strong_text:
                grad_text = (row).find('td').get_text(strip=False) 
                level = check_level(grad_text)

            if "Category" in strong_text:
                type_schol = (row).find('td').text.split()[1]
            
            if "Number Available" in strong_text:
                num_av = (row).find('td').text.split()[2]
                print(num_av,"\n****")
                if num_av.isdigit():
                    num_av = num_av
                elif num_av.lower() not in ["variable", "varies", "up"]:
                    num_av =w2n.word_to_num(num_av)
                value = f"{value}\n{num_av} available"


    
    # Eligibility
    criteria_section = soup.find('div', class_='scholarship-details')
    criteria_section = criteria_section.findAll('li')
    if criteria_section:
        eligibility = [li.get_text(strip=True) for li in criteria_section]
    else:
        eligibility = "Not found"

    create_data_entry(url=create_hyperlink(page_url, scholarship_name), type_of=type_schol, value=value, level=level, criteria=clean_criteria(eligibility), duration=duration, placement=placem)


base_url = "https://scholarships.uow.edu.au"
home_url = "https://scholarships.uow.edu.au/scholarships/listing"

full_response = requests.get(home_url)
soup_main = BeautifulSoup(full_response.content, "html.parser")
sections_all = soup_main.find_all('table', class_='scholarship-listing')

urls = []

for table in sections_all:
    for row in table.find_all('tr'):
        link = row.find('a')
        if link:
            curr_url = concatenate_url(base_url, link['href'])
            search_page(curr_url)
            #break

df = pd.DataFrame(data_raw)         
df['Criteria'] = df['Criteria'].apply(format_criteria)   
df.to_excel("scraped_UOW_data.xlsx", index=False)
