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
import pycountry


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

        @st.cache_data(ttl=60000)
        def zotero_data(library_id, library_type):
            items = zot.everything(zot.top())

            data=[]
            columns = ['Library', 'Link', 'Title','Publication type', 'Abstract', 'Date published', 'Publisher', 'Journal']

            for item in items:
                creators = item['data']['creators']
                creators_str = ", ".join([creator.get('firstName', '') + ' ' + creator.get('lastName', '') for creator in creators])
                data.append((
                    item['library']['name'],
                    item['library']['links']['alternate']['href'],
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

        lib_name = df.iloc[:,0].values[0]
        lib_link = df.iloc[0,1]
        st.subheader(lib_name + ' group library dashboard')
        st.write('Link to library: ' + lib_link)


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
            'forumPost': 'Forum post',
            'document' : 'Document',
            'film' : 'Film',
            'presentation' : 'Presentation',
            'conferencePaper' : 'Conference paper',
            'manuscript' : 'Manuscript'
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

        st.subheader('Publications by type')
        col1, col2 = st.columns(2)
        with col1:
            df_types = pd.DataFrame(df['Publication type'].value_counts())
            df_types = df_types.sort_values(['Publication type'], ascending=[False])
            df_types=df_types.reset_index()
            df_types = df_types.rename(columns={'index':'Publication type','Publication type':'Count'})

            fig = px.pie(df_types, values='Count', names='Publication type')
            fig.update_layout(title={'text':'Item types', 'y':0.95, 'x':0.45, 'yanchor':'top'})
            col1.plotly_chart(fig, use_container_width = True)
        with col2:
            fig = px.bar(df_types, x='Publication type', y='Count', color='Publication type')
            fig.update_layout(
                autosize=False,
                width=1200,
                height=600,)
            fig.update_xaxes(tickangle=-70)
            fig.update_layout(title={'text':'Item types in log scale', 'y':0.95, 'x':0.4, 'yanchor':'top'})
            col2.plotly_chart(fig, use_container_width = True)

        st.write('---')
        st.subheader('Publications overtime')
        col1, col2 = st.columns(2)
        with col1:
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
            col1.plotly_chart(fig, use_container_width = True)

        with col2:
            df_year['Sum'] = df_year['Count'].cumsum()
            fig2 = px.line(df_year, x='Publication year', y='Sum')
            fig2.update_layout(title={'text':'All items in the library by publication year (cumulative sum)', 'y':0.95, 'x':0.5, 'yanchor':'top'})
            fig2.update_layout(
                autosize=False,
                width=1200,
                height=600,)
            fig2.update_xaxes(tickangle=-70)
            col2.plotly_chart(fig2, use_container_width = True)

        st.write('---')
        st.subheader('Journals and publishers')
        col1, col2 = st.columns(2)
        with col1:
            df_journal = df.loc[df['Publication type']=='Journal article']
            df_journal = pd.DataFrame(df_journal['Journal'].value_counts())
            df_journal = df_journal.sort_values(['Journal'], ascending=[False])
            df_journal = df_journal.reset_index()
            df_journal = df_journal.rename(columns={'index':'Journal','Journal':'Count'})

            fig = px.bar(df_journal.head(15), x='Journal', y='Count', color='Journal')
            fig.update_layout(
                autosize=False,
                width=1200,
                height=700,
                showlegend=False)
            fig.update_xaxes(tickangle=-70)
            fig.update_layout(title={'text':'Top 15 Journals', 'y':0.95, 'x':0.4, 'yanchor':'top'})
            col1.plotly_chart(fig, use_container_width = True)

        with col2:
            df_publisher = pd.DataFrame(df['Publisher'].value_counts())
            df_publisher = df_publisher.sort_values(['Publisher'], ascending=[False])
            df_publisher = df_publisher.reset_index()
            df_publisher = df_publisher.rename(columns={'index':'Publisher','Publisher':'Count'})
            df_publisher = df_publisher.fillna('')

            fig = px.bar(df_publisher.head(15), x='Publisher', y='Count', color='Publisher')
            fig.update_layout(
                autosize=False,
                width=1200,
                height=700,
                showlegend=False)
            fig.update_xaxes(tickangle=-70)
            fig.update_layout(title={'text':'Top 15 Publishers', 'y':0.95, 'x':0.4, 'yanchor':'top'})
            col2.plotly_chart(fig, use_container_width = True)

        st.write('---')
        country_map = {
            'british': 'UK',
            'great britain': 'UK',
            'UK' : 'UK', 
            'america' : 'United States',
            'United States of America' : 'United States',
            'Soviet Union': 'Russia', 
            'american' : 'United States',
            'United States' : 'United States',
            'russian' : 'Russia'
            # Add more mappings as needed
        }

        found_countries = {}
        for i, row in df.iterrows():
            title = str(row['Title']).lower()
            for country in pycountry.countries:
                name = country.name.lower()
                if name in title or (name + 's') in title:  # Check for singular and plural forms of country names
                    proper_name = country.name
                    found_countries[proper_name] = found_countries.get(proper_name, 0) + 1
            for non_proper, proper in country_map.items():
                if non_proper in title:
                    found_countries[proper] = found_countries.get(proper, 0) + title.count(non_proper)
        df_countries = pd.DataFrame({'Country': list(found_countries.keys()), 'Count': list(found_countries.values())})
        df_countries

        fig = px.choropleth(df_countries, locations='Country', locationmode='country names', color='Count', 
                    title='Country mentions in titles', color_continuous_scale='Viridis',
                    width=900, height=700) # Adjust the size of the map here
        # Display the map
        fig.show()
        st.plotly_chart(fig, use_container_width=True) 
    else:
        st.error('Write Zotero library ID')