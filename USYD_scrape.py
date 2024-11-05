import requests
import re
import pandas as pd
import pickle
from bs4 import BeautifulSoup

USYD_raw =[]

# Regex
value_pat = r'\$\d{1,3}(?:,\d{3})*'


# Keys
name_omit_keys = ['indigenous', 'aboriginal', 'first nations', 'travel', 'abroad', '404']

##########

def create_data_entry(name="USYD", url="NA", type_of="NA", value="NA", level="NA", criteria="NA", duration="NA", indigenous="No", placement="No"):
    new_entry = {'University': name,
                 'Name': url,
                 'Type': type_of,
                 'Value': value,
                 'Duration': duration,
                 'Level': level,
                 'Criteria': criteria,
                 'Indigenous': indigenous,
                 'Placement': placement}
    USYD_raw.append(new_entry)

def create_hyperlink(page_url, name):
    hyperlink = f'=HYPERLINK("{page_url}", "{name}")'
    return(hyperlink)

# Misses about 15/430. THat's fine can adjust manually
def find_value(soup):
    value = "NA"
    table = soup.find('table')
    if table:
        table_text = table.get_text()
        schol_value = re.findall(value_pat, table_text)
        if schol_value:
            value = schol_value[0]
        
        if "Dean's" in table_text:
            value = "Dean's Discrection"

        if "TBC" in table_text:
            value = "TBC"
    return(value)



def search_page(page_url):
    placement = "No"

    response = requests.get(page_url)
    soup = BeautifulSoup(response.content, "html.parser")

    ## Name
    name_soup = soup.find('h1', class_='pageTitle')
    if name_soup:
        schol_name = name_soup.get_text(strip=True)
    else: 
        return
    if any(key in schol_name.lower() for key in name_omit_keys):
        return

    if "placement" in schol_name.lower():
        placement = "Yes"
    #


    # Value
    schol_val= find_value(soup)
    #

    

    create_data_entry(url=create_hyperlink(page_url, schol_name), placement=placement, value=schol_val)
    return

##########

with open('my_urls.pkl', 'rb') as file:
    url_list = pickle.load(file)
url_list = sorted(url_list)
del url_list[0]


##########

#test_URL = 'https://www.sydney.edu.au/scholarships/e/digital-health-internship.html'
#search_page(test_URL)



test_num = -1

for url in url_list:
    test_num += 1
    print("**Test Page: ", test_num, "  URL: ", url)
    search_page(url)

##########


#print(len(USYD_raw))

df_USYD = pd.DataFrame(USYD_raw)
print(df_USYD['University'])

df_USYD.to_excel("test_USYD.xlsx", index=False)