'''
v simple script to merge
Do this at the end, once I've sorted out manual process for each school
'''

import pandas as pd 

df1 = pd.read_excel('Scholarships Research.xlsx')
df2 = pd.read_excel('scraped_UNSW_data.xlsx')

merged_df = pd.concat([df1, df2], ignore_index=True)

merged_df.to_excel('merged_fule.xlsx', index=False)