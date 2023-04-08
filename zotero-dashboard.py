from pyzotero import zotero
import pandas as pd
import streamlit as st
from IPython.display import HTML
import streamlit.components.v1 as components
import numpy as np
import altair as alt
from pandas.io.json import json_normalize
from datetime import date, timedelta  
import datetime
from streamlit_extras.switch_page_button import switch_page
import plotly.express as px
import numpy as np
import re
import matplotlib.pyplot as plt
import nltk
nltk.download('all')
from nltk.corpus import stopwords
nltk.download('stopwords')
from wordcloud import WordCloud
from gsheetsdb import connect
import gsheetsdb as gdb
import datetime as dt
import time

st.set_page_config(layout = "wide", 
                    page_title='Zotero library dashboard',
                    initial_sidebar_state="auto") 
pd.set_option('display.max_colwidth', None)

st.title("Zotero library dashboard")

with st.sidebar:
    st.image(image, width=150)
    st.sidebar.markdown("# Zotero library dashboard")
    with st.expander('About'):
        st.write('''
        About page
        ''')
        components.html(
        """
        <a rel="license" href="http://creativecommons.org/licenses/by/4.0/"><img alt="Creative Commons Licence" style="border-width:0" 
        src="https://i.creativecommons.org/l/by/4.0/80x15.png" /></a><br />
        © 2022 All rights reserved. This website is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by/4.0/">Creative Commons Attribution 4.0 International License</a>.
        """
        )
    with st.expander('Source code'):
        st.info('''
        Source code of this app is available [here](https://github.com/YusufAliOzkan/zotero-library-dashboard).
        ''')

# Connecting Zotero with API
# library_id = '2514686'
library_id = st.text_input('Write the library id here: ')
library_type = 'group'
api_key = '' # api_key is only needed for private groups and libraries

# Bringing recently changed items

display = st.button('Display dashboard')

if  display:

    zot = zotero.Zotero(library_id, library_type)

    @st.cache_data(ttl=600)
    def zotero_data(library_id, library_type):
        items = zot.everything(zot.top())

        data=[]
        columns = ['Title','Publication type', 'Abstract', 'Date published', 'Publisher', 'Journal']

        for item in items:
            creators = item['data']['creators']
            creators_str = ", ".join([creator.get('firstName', '') + ' ' + creator.get('lastName', '') for creator in creators])
            data.append((
                item['data']['title'], 
                item['data']['itemType'], 
                item['data']['abstractNote'], 
                item['data'].get('date'),
                item['data'].get('publisher'),
                item['data'].get('publicationTitle')
                )) 
        df = pd.DataFrame(data, columns=columns)
        return df

    df = zotero_data(library_id, library_type)

    df['Abstract'] = df['Abstract'].replace(r'^\s*$', np.nan, regex=True) # To replace '' with NaN. Otherwise the code below do not understand the value is nan.
    df['Abstract'] = df['Abstract'].fillna('No abstract')

    # Change type name
    type_map = {
        'thesis': 'Thesis',
        'journalArticle': 'Journal article',
        'book': 'Book',
        'bookSection': 'Book chapter',
        'blogPost': 'Blog post',
        'videoRecording': 'Video',
        'podcast': 'Podcast',
        'magazineArticle': 'Magazine article',
        'webpage': 'Webpage',
        'newspaperArticle': 'Newspaper article',
        'report': 'Report',
        'forumPost': 'Forum post'
    }
    df['Publication type'] = df['Publication type'].replace(type_map)

    df['Date published'] = pd.to_datetime(df['Date published'], errors='coerce')
    df['Date published'] = pd.to_datetime(df['Date published'],utc=True).dt.tz_convert('Europe/London')
    df['Date published'] = df['Date published'].dt.strftime('%d-%m-%Y')
    df['Date published'] = df['Date published'].fillna('No date')
    # df['Date published'] = df['Date published'].map(lambda x: x.strftime('%d/%m/%Y') if x else 'No date')

    df