
import streamlit as st
import pandas as pd
from bs4 import BeautifulSoup
import requests, lxml, os


headers = {
    'User-agent':
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.19582"
}

proxies = {
  'http': os.getenv('HTTP_PROXY')
}

def get_profile_1(ORGID):
  html = requests.get(f'https://scholar.google.com/citations?view_op=view_org&hl=en&org={ORGID}', headers=headers, proxies=proxies).text

  soup = BeautifulSoup(html, 'lxml')

  entry_list = {'Name':[],'ID':[],'Affiliation':[], 'Interests':[], 'Citations':[]}

  for result in soup.select('.gs_ai_chpr'):
    name = result.select_one('.gs_ai_name a').text
    gsID = result.select_one('.gs_ai_name a')['href'].strip('/citations?hl=en&user=')
    affiliations = result.select_one('.gs_ai_aff').text

    try:
      interests = result.select_one('.gs_ai_one_int').text
    except:
      interests = None
    citations = result.select_one('.gs_ai_cby').text.split(' ')[2]
    
    entry_list['Name'].append(name)
    entry_list['ID'].append(gsID)
    entry_list['Affiliation'].append(affiliations)
    entry_list['Interests'].append(interests)
    entry_list['Citations'].append(citations)

  df = pd.DataFrame(entry_list)
  
  return df

def get_profile_2(ORGID, next_link, page_index):
  html = requests.get(f'https://scholar.google.com/citations?view_op=view_org&hl=en&org={ORGID}&after_author={next_link}&astart={page_index}', headers=headers, proxies=proxies).text
  soup = BeautifulSoup(html, 'lxml')

  entry_list = {'Name':[],'ID':[],'Affiliation':[], 'Interests':[], 'Citations':[]}

  for result in soup.select('.gs_ai_chpr'):
    name = result.select_one('.gs_ai_name a').text
    gsID = result.select_one('.gs_ai_name a')['href'].strip('/citations?hl=en&user=')
    affiliations = result.select_one('.gs_ai_aff').text

    try:
      interests = result.select_one('.gs_ai_one_int').text
    except:
      interests = None
    citations = result.select_one('.gs_ai_cby').text.split(' ')[2]
    
    entry_list['Name'].append(name)
    entry_list['ID'].append(gsID)
    entry_list['Affiliation'].append(affiliations)
    entry_list['Interests'].append(interests)
    entry_list['Citations'].append(citations)

  df = pd.DataFrame(entry_list)
  
  return df

# Retrieves the next link from the Google Scholar Profile page

def get_next_link_1(ORGID):
  html = requests.get(f'https://scholar.google.com/citations?view_op=view_org&hl=en&org={ORGID}', headers=headers, proxies=proxies).text
  soup = BeautifulSoup(html, 'lxml')
  btn = soup.find('button', {'aria-label': 'Next'})
  btn_onclick = btn['onclick']
  next_link = btn_onclick.split('\\')[-3].lstrip('x3d')
  return next_link

# Retrieves the next link from the Google Scholar Profile page
def get_next_link_2(ORGID, next_link, page_index):
  html = requests.get(f'https://scholar.google.com/citations?view_op=view_org&hl=en&org={ORGID}&after_author={next_link}&astart={page_index}', headers=headers, proxies=proxies).text
  soup = BeautifulSoup(html, 'lxml')
  btn = soup.find('button', {'aria-label': 'Next'})
  btn_onclick = btn['onclick']
  #next_link = btn_onclick.split('\\')[-3].lstrip('x3d')
  next_link = btn_onclick.split('\\')[-3][3:]
  return next_link

# Display app content

st.set_page_config(layout='wide')

st.markdown('''
# Google Scholar Clone App 📚
This App retrieves researcher citation data from *****Google Scholar***** for Few Indian Engineering Colleges.
''')

st.sidebar.header('Scholar App Settings')

org_list = {'Thapar University':'127941673281695664',
            'Chitkara University':'5634525332006733526',
            'Lovely Professional University':'288173882962095775',
            'Indian Institute of Technology, Delhi':'9685961713560283847',
            'Indian Institute of Technology, Ropar':'12445371738883199202',
            'Indian Institute of Technology, Bombay':'15559271020991466530',
            'Birla Institute of Technology and Science, Pilani':'1214501747206074955',
            'Indian Institute of Technology, Roorkee':'4137058844232715996',
            "Delhi Technological University":"3848567308418696316"}

orgid = st.sidebar.selectbox('Select a University', 
                              ('Thapar University', 
                              'Chitkara University', 
                              'Lovely Professional University',
                              'Indian Institute of Technology, Delhi',
                              'Indian Institute of Technology, Ropar',
                              'Indian Institute of Technology, Bombay',
                              'Birla Institute of Technology and Science, Pilani',
                              'Indian Institute of Technology, Roorkee',
                              "Delhi Technological University") )
orgid = org_list[orgid]

query_size = st.sidebar.slider('Select No. of Resarchers', 10, 100, 10, 5)
query_size = int(query_size/10)

p_index = 10
df_list = []

for i in range(query_size):
  if i == 0:
    df1 = get_profile_1(orgid)
    df_list.append(df1)
    nxt_link_1 = get_next_link_1(orgid)
    #p_index += 10
    print(nxt_link_1, p_index)
  if i == 1:
    df2 = get_profile_2(orgid, nxt_link_1, p_index)
    nxt_link_2 = get_next_link_2(orgid, nxt_link_1, p_index)
    df_list.append(df2)
    p_index += 10
    print(nxt_link_2, p_index)
  if i > 1:
    df3 = get_profile_2(orgid, nxt_link_2, p_index)
    nxt_link_2 = get_next_link_2(orgid, nxt_link_2, p_index)
    df_list.append(df3)
    p_index += 10
    print(nxt_link_2, p_index)

df = pd.concat(df_list)
df.reset_index(drop=True, inplace=True)

df
