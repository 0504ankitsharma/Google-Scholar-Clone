# Google Scholar Clone App 📚

This Streamlit application is a simplified version of Google Scholar that retrieves and analyzes citation data for researchers from various Indian engineering colleges. Users can navigate through different sections of the app using the sidebar menu.

## Features

- **Data Retrieval**: Fetch data of researchers from selected Indian engineering colleges based on specified criteria such as number of researchers and minimum number of citations.
- **Analytics**: Visualize citation distribution and view the top 10 researchers by citations.
- **Download**: Download fetched data as CSV or Excel files.

## Requirements

- Python 3.7 or higher
- Install the required packages using `pip install -r requirements.txt`

## Usage

1. Run the Streamlit app using the command `streamlit run app.py`.
2. Navigate through different sections using the sidebar menu.
3. On the Data Retrieval page, select a university, specify the number of researchers, minimum number of citations, and sorting criteria, then click "Fetch Data".
4. Once data is fetched, explore analytics and download options on the respective pages.

## Dependencies

- [Streamlit](https://streamlit.io/)
- [Pandas](https://pandas.pydata.org/)
- [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/)
- [Requests](https://docs.python-requests.org/en/master/)
- [Plotly](https://plotly.com/python/)
- [Streamlit Option Menu](https://pypi.org/project/streamlit-option-menu/)
