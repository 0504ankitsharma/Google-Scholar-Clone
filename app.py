import streamlit as st
import pandas as pd
from bs4 import BeautifulSoup
import requests, os
import plotly.express as px
from streamlit_option_menu import option_menu

st.set_page_config(page_title="Google Scholar Clone App", page_icon="📚")

# Define headers and proxies
headers = {
    'User-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.19582"
}

proxies = {
  'http': os.getenv('HTTP_PROXY')
}

# Function to get profile data from Google Scholar
def get_profile(ORGID, next_link=None, page_index=0):
    url = f'https://scholar.google.com/citations?view_op=view_org&hl=en&org={ORGID}'
    if next_link:
        url += f'&after_author={next_link}&astart={page_index}'
    
    html = requests.get(url, headers=headers, proxies=proxies).text
    soup = BeautifulSoup(html, 'lxml')

    entry_list = {'Name': [], 'ID': [], 'Affiliation': [], 'Interests': [], 'Citations': []}

    for result in soup.select('.gs_ai_chpr'):
        name = result.select_one('.gs_ai_name a').text
        gsID = result.select_one('.gs_ai_name a')['href'].split('user=')[1]
        affiliations = result.select_one('.gs_ai_aff').text
        interests = result.select_one('.gs_ai_one_int').text if result.select_one('.gs_ai_one_int') else None
        citations = int(result.select_one('.gs_ai_cby').text.split(' ')[2])
        
        entry_list['Name'].append(name)
        entry_list['ID'].append(gsID)
        entry_list['Affiliation'].append(affiliations)
        entry_list['Interests'].append(interests)
        entry_list['Citations'].append(citations)

    df = pd.DataFrame(entry_list)
    return df, soup

# Function to get the next link for pagination
def get_next_link(soup):
    btn = soup.find('button', {'aria-label': 'Next'})
    if btn:
        btn_onclick = btn['onclick']
        next_link = btn_onclick.split('\\')[-3].lstrip('x3d')
        return next_link
    return None

# Define the sidebar menu
with st.sidebar:
    selected = option_menu(
        menu_title="Main Menu",
        options=["Home", "Data Retrieval", "Analytics", "Download"],
        icons=["house", "search", "bar-chart-line", "download"],
        menu_icon="cast",
        default_index=0,
        styles={
            "container": {"padding": "5px", "background-color": "#333333"},
            "icon": {"color": "#FFFFFF", "font-size": "25px"}, 
            "nav-link": {"font-size": "16px", "text-align": "left", "margin": "0px", "--hover-color": "#444444"},
            "nav-link-selected": {"background-color": "#FFD700"},
        }
    )

# Home Page
if selected == "Home":
    st.title("Welcome to Google Scholar Clone App 📚")
    st.markdown('''
    <div style="text-align: justify;">
        This application retrieves and analyzes researcher citation data from <b>Google Scholar</b> for several Indian Engineering Colleges.
        Use the sidebar to navigate through different sections of the app.
    </div>
    ''', unsafe_allow_html=True)

# Data Retrieval Page
elif selected == "Data Retrieval":
    st.title("Data Retrieval")
    
    org_list = {
        'Thapar University': '127941673281695664',
        'Chitkara University': '5634525332006733526',
        'Lovely Professional University': '288173882962095775',
        'Indian Institute of Technology, Delhi': '9685961713560283847',
        'Indian Institute of Technology, Ropar': '12445371738883199202',
        'Indian Institute of Technology, Bombay': '15559271020991466530',
        'Birla Institute of Technology and Science, Pilani': '1214501747206074955',
        'Indian Institute of Technology, Roorkee': '4137058844232715996',
        "Delhi Technological University": "3848567308418696316"
    }

    orgid = st.selectbox('Select a University', list(org_list.keys()))
    orgid = org_list[orgid]

    query_size = st.slider('Select Number of Researchers', 10, 100, 10, 5)
    min_citations = st.number_input('Minimum Number of Citations', min_value=0, value=0, step=1)
    sort_by = st.selectbox('Sort By', ['Name', 'Citations'])

    if st.button("Fetch Data"):
        with st.spinner('Fetching data...'):
            df_list = []
            next_link = None
            page_index = 0

            for i in range(query_size // 10):
                df, soup = get_profile(orgid, next_link, page_index)
                df_list.append(df)
                next_link = get_next_link(soup)
                page_index += 10
                if not next_link:
                    break

            df = pd.concat(df_list).reset_index(drop=True)

            # Apply filters
            df = df[df['Citations'] >= min_citations]

            # Sort data
            if sort_by == 'Name':
                df = df.sort_values(by='Name')
            else:
                df = df.sort_values(by='Citations', ascending=False)

            st.dataframe(df.style.format({"Citations": "{:.0f}"}))
            st.session_state['df'] = df

# Analytics Page
elif selected == "Analytics":
    st.title("Analytics")

    if 'df' in st.session_state:
        df = st.session_state['df']
        
        st.subheader("Citations Distribution")
        fig = px.histogram(df, x='Citations', nbins=20, title='Citations Distribution', template='plotly_dark')
        st.plotly_chart(fig)

        st.subheader("Top 10 Researchers by Citations")
        top_10 = df.nlargest(10, 'Citations')
        fig = px.bar(top_10, x='Name', y='Citations', title='Top 10 Researchers by Citations', template='plotly_dark')
        st.plotly_chart(fig)
    else:
        st.warning("Please fetch data first from the Data Retrieval page.")

# Download Page
elif selected == "Download":
    st.title("Download Data")

    if 'df' in st.session_state:
        df = st.session_state['df']
        
        st.download_button(
            label="Download Data as CSV",
            data=df.to_csv(index=False),
            file_name='scholar_data.csv',
            mime='text/csv'
        )

        st.download_button(
            label="Download Data as Excel",
            data=df.to_excel(index=False),
            file_name='scholar_data.xlsx',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    else:
        st.warning("Please fetch data first from the Data Retrieval page.")

# Custom CSS for enhanced UI
st.markdown("""
    <style>
        .css-1d391kg {
            padding: 1rem;
            background-color: #282828;
            border-radius: 10px;
            color: white;
        }
        .stButton button {
            background-color: #FFD700;
            color: #333333;
            border-radius: 5px;
        }
        footer {
            visibility: hidden;
        }
        footer:after {
            content:'Google Scholar Clone App by Your Name'; 
            visibility: visible;
            display: block;
            position: relative;
            padding: 5px;
            top: 2px;
            text-align: center;
            background-color: #333333;
            color: #FFD700;
        }
        .main .block-container {
            padding-top: 2rem;
            color: white;
        }
    </style>
""", unsafe_allow_html=True)
