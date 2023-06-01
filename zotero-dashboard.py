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
import spacy
import ast
from spacy.pipeline import EntityRecognizer
import pyzotero.zotero_errors


st.set_page_config(layout = "wide", 
                    page_title='Zotero library dashboard',
                    initial_sidebar_state="auto") 
pd.set_option('display.max_colwidth', None)

st.title("Zotero library dashboard")
st.write('View your Zotero library in a dashboard! All you need to do is to find the Zotero group library (or group ID) or your Zotero personal library credentials and paste it below.')
 
with st.sidebar:
    image = 'https://upload.wikimedia.org/wikipedia/commons/thumb/7/74/Zotero_logo.svg/1920px-Zotero_logo.svg.png'
    st.image(image, width=150)
    st.sidebar.markdown("# Zotero library dashboard")
    with st.expander('About'):
        st.write('''
        This app shows a dashboard of Zotero group libraries. Enter the group library link or ID and click 'Display dashboard' to see visuals of the library.
        ''')

        st.write('This app was built and is managed by [Yusuf Ozkan](https://www.kcl.ac.uk/people/yusuf-ali-ozkan) | [Twitter](https://twitter.com/yaliozkan) | [LinkedIn](https://www.linkedin.com/in/yusuf-ali-ozkan/) | [ORCID](https://orcid.org/0000-0002-3098-275X) | [GitHub](https://github.com/YusufAliOzkan)')

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
try:
    choice = st.radio('Type of the library: ', ('Group library (use group library link)', 'Group library (use group library id)', 'Personal library'))

    if choice == 'Group library (use group library link)':
        st.caption('Search Zotero group libraries [here](https://www.zotero.org/search/type/group) or try the following link as an example: https://www.zotero.org/groups/2514686/intelligence_bibliography')
        library_id = st.text_input('Group library link: ')
        df = pd.DataFrame({'link': [library_id]})
        library_id = df['link'].str.extract(r'groups/(\d+)/').iloc[0, 0]
        library_type = 'group'

    elif choice == 'Group library (use group library id)': 
        library_id = st.text_input('Group library id: ')
        library_id = library_id.replace(' ', '')
        st.caption('Write 2514686 as an example.')
        library_type = 'group'
    
    else:
        library_id = st.text_input('Personal library ID: ')
        api_key = st.text_input('Zotero API key: ([Find here](https://www.zotero.org/settings/keys/new)): ')
        library_type = 'user'


    # api_key = '' # api_key is only needed for private groups and libraries

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
            st.subheader("'"+lib_name + "' Zotero "+ library_type + " library dashboard")
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
                df_journal = df_journal.dropna()
                df_journal['Journal'] = df_journal['Journal'].str[:50]

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
            st.subheader('Countries mentioned in titles')
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
            
            if df_countries.empty:
                st.write('No country mentioned in title')

            else:
                fig = px.choropleth(df_countries, locations='Country', locationmode='country names', color='Count', 
                            title='Country mentions in titles', color_continuous_scale='Viridis',
                            width=900, height=700) # Adjust the size of the map here
                # Display the map
                fig.show()
                st.plotly_chart(fig, use_container_width=True) 

            st.write('---')
            def clean_text (text):
                text = text.lower() # lowercasing
                text = re.sub(r'[^\w\s]', ' ', text) # this removes punctuation
                text = re.sub('[0-9_]', ' ', text) # this removes numbers
                text = re.sub('[^a-z_]', ' ', text) # removing all characters except lowercase letters
                return text
            df['clean_title'] = df['Title'].apply(clean_text)
            df['clean_abstract'] = df['Abstract'].astype(str).apply(clean_text)
            df_abs_no = df.dropna(subset=['clean_abstract'])
            df['clean_title'] = df['clean_title'].apply(lambda x: ' '.join ([w for w in x.split() if len (w)>2])) # this function removes words less than 2 words
            df['clean_abstract'] = df['clean_abstract'].apply(lambda x: ' '.join ([w for w in x.split() if len (w)>2])) # this function removes words less than 2 words

            def tokenization(text):
                text = re.split('\W+', text)
                return text
            df['token_title']=df['clean_title'].apply(tokenization)
            df['token_abstract']=df['clean_abstract'].apply(tokenization)
            stopword = nltk.corpus.stopwords.words('english')

            SW = ['york', 'intelligence', 'security', 'pp', 'war','world', 'article', 'twitter', 'nan',
                'new', 'isbn', 'book', 'also', 'yet', 'matter', 'erratum', 'commentary', 'studies',
                'volume', 'paper', 'study', 'question', 'editorial', 'welcome', 'introduction', 'editorial', 'reader',
                'university', 'followed', 'particular', 'based', 'press', 'examine', 'show', 'may', 'result', 'explore',
                'examines', 'become', 'used', 'journal', 'london', 'review', 'abstract']
            stopword.extend(SW)

            def remove_stopwords(text):
                text = [i for i in text if i] # this part deals with getting rid of spaces as it treads as a string
                text = [word for word in text if word not in stopword] #keep the word if it is not in stopword
                return text
            df['stopword']=df['token_title'].apply(remove_stopwords)
            df['stopword_abstract']=df['token_abstract'].apply(remove_stopwords)

            wn = nltk.WordNetLemmatizer()
            def lemmatizer(text):
                text = [wn.lemmatize(word) for word in text]
                return text

            df['lemma_title'] = df['stopword'].apply(lemmatizer) # error occurs in this line
            df['lemma_abstract'] = df['stopword_abstract'].apply(lemmatizer) # error occurs in this line

            listdf = df['lemma_title']
            listdf_abstract = df['lemma_abstract']

            st.subheader('Wordcloud')
            col1, col2 = st.columns(2)
            with col1:
                df_list = [item for sublist in listdf for item in sublist]
                string = pd.Series(df_list).str.cat(sep=' ')
                wordcloud_texts = string
                wordcloud_texts_str = str(wordcloud_texts)
                wordcloud = WordCloud(stopwords=stopword, width=1500, height=750, background_color='white', collocations=False, colormap='magma').generate(wordcloud_texts_str)
                plt.figure(figsize=(20,8))
                plt.axis('off')
                plt.title('Top words in title (Intelligence bibliography collection)')
                plt.imshow(wordcloud)
                plt.axis("off")
                plt.show()
                st.set_option('deprecation.showPyplotGlobalUse', False)
                col1.pyplot() 
            with col2:
                df_list_abstract = [item for sublist in listdf_abstract for item in sublist]
                string = pd.Series(df_list_abstract).str.cat(sep=' ')
                wordcloud_texts = string
                wordcloud_texts_str = str(wordcloud_texts)
                wordcloud = WordCloud(stopwords=stopword, width=1500, height=750, background_color='white', collocations=False, colormap='magma').generate(wordcloud_texts_str)
                plt.figure(figsize=(20,8))
                plt.axis('off')
                plt.title('Top words in abstract (Intelligence bibliography collection)')
                plt.imshow(wordcloud)
                plt.axis("off")
                plt.show()
                st.set_option('deprecation.showPyplotGlobalUse', False)
                col2.pyplot()  
            st.warning('Please bear in mind that not all items listed in this bibliography have an abstract.')

            st.write('---')
            st.subheader('Entities')
            st.caption('This part uses [NER](https://en.wikipedia.org/wiki/Named-entity_recognition)')
            nltk.download('punkt')
            nltk.download('averaged_perceptron_tagger')
            nltk.download('maxent_ne_chunker')
            nltk.download('words')
            spacy.cli.download("en_core_web_sm")
            nlp = spacy.load("en_core_web_sm")
            ruler = nlp.add_pipe("entity_ruler")
            patterns = [{"label": "ORG", "pattern": "MI6"}]
            ruler.add_patterns(patterns)
            @st.cache_data(ttl=6000)
            def extract_entities(text):
                doc = nlp(text)
                orgs = []
                gpes = []
                people = []
                for entity in doc.ents:
                    if entity.label_ == 'ORG':
                        orgs.append(entity.text)
                    elif entity.label_ == 'GPE':
                        gpes.append(entity.text)
                    elif entity.label_ == 'PERSON':
                        people.append(entity.text)
                return pd.Series({'ORG': orgs, 'GPE': gpes, 'PERSON': people})
            df_title = df[['Title']].copy()
            df_title = df_title.rename(columns={'Title':'Text'})
            df_abstract = df[['Abstract']].copy()
            df_abstract = df_abstract.rename(columns={'Abstract':'Text'})
            df_one = pd.concat([df_title, df_abstract], ignore_index=True)
            df_one['Text'] = df_one['Text'].fillna('')
            df_one = pd.concat([df_one[['Text']], df_one['Text'].apply(extract_entities)], axis=1)
            df_one = df_one.explode('GPE').reset_index(drop=True)
            df_one = df_one.explode('ORG').reset_index(drop=True)
            df_one = df_one.explode('PERSON').reset_index(drop=True)

            df_one_g = df_one.copy()
            df_one_g = df_one[['Text', 'GPE']]
            df_one_g = df_one_g.drop_duplicates(subset=['Text', 'GPE'])
            gpe_counts = df_one_g['GPE'].value_counts().reset_index()
            gpe_counts.columns = ['GPE', 'count']
            mapping_locations = {
                'the United States': 'USA',
                'The United States': 'USA',
                'US': 'USA',
                'U.S.': 'USA',
                'United States' : 'USA',
                'America' : 'USA',
                'the United States of America' : 'USA',
                'Britain' : 'UK',
                'the United Kingdom': 'UK',
                'U.K.' : 'UK',
                'Global Britain' : 'UK',
                'United Kingdom' : 'UK', 
                'the Soviet Union' : 'Russia',
                'The Soviet Union' : 'Russia',
                'USSR' : 'Russia',
                'Ukraine - Perspective' : 'Ukraine',
                'Ukrainian' : 'Ukraine',
                'Great Britain' : 'UK',
                'Ottoman Empire' : 'Turkey'
            }
            gpe_counts['GPE'] =gpe_counts['GPE'].replace(mapping_locations)
            gpe_counts = gpe_counts.groupby('GPE').sum().reset_index()
            gpe_counts.sort_values('count', ascending=False, inplace=True)
            gpe_counts.reset_index(drop=True)

            df_one_p = df_one.copy()
            df_one_p = df_one[['Text', 'PERSON']]
            # df_one_p = df_one_g.fillna('')
            df_one_p = df_one_p.drop_duplicates(subset=['Text', 'PERSON'])
            person_counts = df_one_p['PERSON'].value_counts().reset_index()
            person_counts.columns = ['PERSON', 'count']
            person_counts = person_counts.groupby('PERSON').sum().reset_index()
            person_counts.sort_values('count', ascending=False, inplace=True)
            person_counts = person_counts.reset_index(drop=True)

            df_one_o = df_one.copy()
            df_one_o = df_one[['Text', 'ORG']]
            # df_one_p = df_one_g.fillna('')
            df_one_o = df_one_o.drop_duplicates(subset=['Text', 'ORG'])
            org_counts = df_one_o['ORG'].value_counts().reset_index()
            org_counts.columns = ['ORG', 'count']
            org_counts = org_counts.groupby('ORG').sum().reset_index()
            org_counts.sort_values('count', ascending=False, inplace=True)
            org_counts = org_counts.reset_index(drop=True)

            col1, col2, col3 = st.columns(3)
            with col1:
                fig = px.bar(gpe_counts.head(15), x='GPE', y='count', height=600, title="Top 15 locations mentioned in title & abstract")
                fig.update_xaxes(tickangle=-65)
                col1.plotly_chart(fig, use_container_width=True)
            with col2:
                fig = px.bar(person_counts.head(15), x='PERSON', y='count', height=600, title="Top 15 person mentioned in title & abstract")
                fig.update_xaxes(tickangle=-65)
                col2.plotly_chart(fig, use_container_width=True)
            with col3:
                fig = px.bar(org_counts.head(15), x='ORG', y='count', height=600, title="Top 15 organisations mentioned in title & abstract")
                fig.update_xaxes(tickangle=-65)
                col3.plotly_chart(fig, use_container_width=True)
            
except pyzotero.zotero_errors.HTTPError as e:
    st.error("This doesn't look like the correct link or ID. Also, the libary may not be public. In that case, this app won't be able to display dashboard.".format(e))
except pyzotero.zotero_errors.UserNotAuthorised as e:
    st.error("You are not authorized to access this library. Please check your credentials and try again.")
except pyzotero.zotero_errors.MissingCredentials as e:
    st.error("Credentials are missing. Please provide the Zotero group library ID.")
except pyzotero.zotero_errors.ResourceNotFound:
    st.error("This doesn't look like the correct link or ID. Also, the libary may not be public. In that case, this app won't be able to display dashboard.")

components.html(
"""
<a rel="license" href="http://creativecommons.org/licenses/by/4.0/"><img alt="Creative Commons Licence" style="border-width:0" 
src="https://i.creativecommons.org/l/by/4.0/80x15.png" /></a><br />
© 2022 All rights reserved. This website is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by/4.0/">Creative Commons Attribution 4.0 International License</a>.
"""
)  