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

with st.spinner('Creating dashboard. This may take a while if the library contains more items.'):
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

        groups = zot.groups()
        for group in groups:
            st.write(f"Name: {group['data']['name']}")

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

        df['Date published'] = pd.to_datetime(df['Date published'],utc=True, errors='coerce').dt.tz_convert('Europe/London')
        df['Date year'] = df['Date published'].dt.strftime('%Y')
        df['Date year'] = df['Date year'].fillna('No date')
        with st.expander('See dataset'):
            df

        st.subheader('Publications overtime')
        df_year = df['Date year'].value_counts()
        df_year = df_year.reset_index()
        df_year=df_year.rename(columns={'index':'Publication year','Date year':'Count'})
        df_year.drop(df_year[df_year['Publication year']== 'No date'].index, inplace = True)
        df_year=df_year.sort_values(by='Publication year', ascending=True)
        df_year=df_year.reset_index(drop=True)
        fig = px.bar(df_year, x='Publication year', y='Count')
        fig.update_layout(
            autosize=False,
            width=1200,
            height=600,)
        fig.update_layout(title={'text':'All items in the library by publication year', 'y':0.95, 'x':0.5, 'yanchor':'top'})
        st.plotly_chart(fig, use_container_width = True)



    else:
        st.error('Write Zotero library ID')