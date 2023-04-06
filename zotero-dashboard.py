import streamlit as st
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
import pandas as pd
import pyperclip
import streamlit.components.v1 as components


# Exporting dataset
df = pd.read_csv(r'statements.csv')
df['publisher'] = df['publisher'].astype(str)
df['link'] = df['link'].astype(str)
df['link'] = df['link'].replace('nan', 'No link found')

df_rrs = df.copy()
df['statement'] = 'Copyright ' + df['statement'].astype(str)
df_new=df.sort_values(by='publisher')

# Setting the app page layout
st.set_page_config(
    layout = "wide", 
    page_title='CAPS tool', 
    page_icon="https://upload.wikimedia.org/wikipedia/commons/thumb/b/b0/Copyright.svg/220px-Copyright.svg.png",
    menu_items={
        'About': "This tool lists different copyright and publisher set statements and allows users to copy the statements to their clipboard. You can select the publisher statements from the dropdown menu or find the Frequently used publisher statements. You can also find an example of rights retention statement if you wish to add it to your submitted manuscript. The tool also has a quick citation generator for ‘grey literature’ items. Source code of this app is available [here](https://github.com/YusufAliOzkan/copyright_statements)."
    }
)
path='https://upload.wikimedia.org/wikipedia/en/thumb/3/32/Logo_for_Imperial_College_London.svg/2560px-Logo_for_Imperial_College_London.svg.png'
path2 = 'https://upload.wikimedia.org/wikipedia/commons/thumb/b/b0/Copyright.svg/220px-Copyright.svg.png'
# st.image(path2, width=75)    
st.markdown("# CAPS (Copyright and Publisher Statements) tool")

with st.sidebar:
    st.image(path2, width=150)
    st.markdown("# CAPS tool")  
    with st.expander('About'):  
        st.write('This tool lists different copyright and publisher set statements and allows users to copy the statements to their clipboard. You can select the publisher statements from the dropdown menu or find the Frequently used publisher statements. You can also find an example of rights retention statement if you wish to add it to your submitted manuscript. The tool also has a quick citation generator for ‘grey literature’ items.')
        st.write('Contact us if you have any questions, comments or questions!')
        components.html(
"""
<a rel="license" href="http://creativecommons.org/licenses/by/4.0/"><img alt="Creative Commons Licence" style="border-width:0" src="https://i.creativecommons.org/l/by/4.0/80x15.png" /></a><br />This tool is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by/4.0/">Creative Commons Attribution 4.0 International License</a>.
"""
)

    with st.expander('Source code'):
        st.info('CAPSv1.2. Source code of this app is available [here](https://github.com/YusufAliOzkan/copyright_statements).')
    with st.expander('Disclaimer'):
        st.warning('Please note that although every effort has been made to keep this list updated, there might be missing, incomplete, or not updated information. If you believe something is wrong, please feel free to get in touch.', icon="ℹ️")
    with st.expander('Contact us'):
        st.write("**Get in touch!**")   
        contact_form = """
        <form action="https://formsubmit.co/yusufaliozkan37@gmail.com" method="POST">
            <input type="hidden" name="_captcha" value="false">
            <input type="text" name="name" placeholder="Your name" required>
            <input type="email" name="email" placeholder="Your email" required>
            <textarea name="message" placeholder="Your message here"></textarea>
            <button type="submit">Send</button>
        </form>
        """

        st.markdown(contact_form, unsafe_allow_html=True)

        # Use Local CSS File
        def local_css(file_name):
            with open(file_name) as f:
                st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    local_css("style.css")

tab1, tab2, tab3 = st.tabs(['Publisher and copyright statements', 'Rights retention statement', 'Grey literature citation generator'])

with tab1:
    st.subheader('Publisher and copyright statements')
    st.write('This page lists set publisher statements that need to accompany self-archiving in institutional repositories. From the dropdown menu, select the publisher and then copy the statement to clipboard.')
    
    col1, col2 = st.columns([1,2])
    with col1:

        clist = df_new['publisher'].unique()
        publisher = st.selectbox("Select a publisher:",clist)
        df_statement = df.loc[df_new['publisher']==publisher, 'statement'].values[0]
        df_link = df.loc[df['publisher']==publisher, 'link'].values[0]
    with col2:
        st.write('**Statement for:** ' + publisher)
        st.write('Link to statement: ' + df_link)
        st.info(df_statement)

        text_to_be_copied = df_statement
        copy_dict = {"content": text_to_be_copied}

        copy_button = Button(label="Copy to clipboard")
        copy_button.js_on_event("button_click", CustomJS(args=copy_dict, code="""
            navigator.clipboard.writeText(content);
            """))

        no_event = streamlit_bokeh_events(
            copy_button,
            events="GET_TEXT",
            key="get_text",
            refresh_on_update=True,
            override_height=75,
            debounce_time=0)
        
    st.subheader('Frequently used statements')
    col1, col2 = st.columns([1,2])
    with col1:
        df_frequent = df.loc[df_new['publisher'].isin(['Elsevier', 'Wiley', 'Springer Nature', 'IEEE ', 'SAGE Publications', 'BMJ Publishing', 'Oxford University Press (OUP)', 'American Chemical Society'])]
        frequently = st.radio('Choose a publisher to display the statement', df_frequent['publisher']) #('Elsevier', 'Wiley', 'Springer Nature', 'IEEE', 'SAGE Publications', 'BMJ Publishing', 'Oxford University Press (OUP)', 'American Chemical Society'))
        text_to_be_copied = df.loc[df_new['publisher']==frequently, 'statement'].values[0]

    with col2:
        st.write('**Statement for:** ' + frequently)
        st.caption(text_to_be_copied)

        copy_dict = {"content": text_to_be_copied} 

        copy_button = Button(label="Copy to clipboard")
        copy_button.js_on_event("button_click", CustomJS(args=copy_dict, code="""
            navigator.clipboard.writeText(content);
            """))

        no_event = streamlit_bokeh_events(
            copy_button,
            events="GET_TEXTfu1",
            key="get_textfu1",
            refresh_on_update=True,
            override_height=75,
            debounce_time=0)

    col1, col2 = st.columns([1,2])
    with col1:
        df_copyright = df.loc[df_new['publisher'].isin(['CC BY licence', 'CC BY-NC licence', 'CC BY-NC-ND licence', 'CC BY-NC-SA licence', 'CC BY-SA licence'])]
        copyright = st.radio('Choose a CC licence to display the statement', df_copyright['publisher']) 
        text_to_be_copied2 = df.loc[df_new['publisher']==copyright, 'statement'].values[0]

    with col2:
        st.write('**Statement for:** ' + copyright)
        st.caption(text_to_be_copied2)

        copy_dict = {"content": text_to_be_copied2} 

        copy_button = Button(label="Copy to clipboard")
        copy_button.js_on_event("button_click", CustomJS(args=copy_dict, code="""
            navigator.clipboard.writeText(content);
            """))

        no_event = streamlit_bokeh_events(
            copy_button,
            events="GET_TEXTfu2",
            key="get_textfu2",
            refresh_on_update=True,
            override_height=75,
            debounce_time=0)

    # show = st.checkbox('Display statements')

    # col1, col2, col3, col4 = st.columns(4)

    # with col1:
    #     text_to_be_copied = df.loc[df_new['publisher']=='Elsevier', 'statement'].values[0]
    #     copy_dict = {"content": text_to_be_copied}

    #     copy_button = Button(label="Elsevier")
    #     copy_button.js_on_event("button_click", CustomJS(args=copy_dict, code="""
    #         navigator.clipboard.writeText(content);
    #         """))

    #     no_event = streamlit_bokeh_events(
    #         copy_button,
    #         events="GET_TEXTqqq",
    #         key="get_textqqq",
    #         refresh_on_update=True,
    #         override_height=75,
    #         debounce_time=0)
    #     if show:
    #         st.caption(text_to_be_copied)

    # with col2:
    #     text_to_be_copied = df.loc[df_new['publisher']=='Wiley', 'statement'].values[0]
    #     copy_dict = {"content": text_to_be_copied}

    #     copy_button = Button(label="Wiley")
    #     copy_button.js_on_event("button_click", CustomJS(args=copy_dict, code="""
    #         navigator.clipboard.writeText(content);
    #         """))

    #     no_event = streamlit_bokeh_events(
    #         copy_button,
    #         events="GET_TEXTwww",
    #         key="get_textwww",
    #         refresh_on_update=True,
    #         override_height=75,
    #         debounce_time=0)
    #     if show:
    #         st.caption(text_to_be_copied)

    # with col3:
    #     text_to_be_copied = df.loc[df_new['publisher']=='Springer Nature', 'statement'].values[0]
    #     copy_dict = {"content": text_to_be_copied}

    #     copy_button = Button(label="Springer Nature")
    #     copy_button.js_on_event("button_click", CustomJS(args=copy_dict, code="""
    #         navigator.clipboard.writeText(content);
    #         """))

    #     no_event = streamlit_bokeh_events(
    #         copy_button,
    #         events="GET_TEXT5",
    #         key="get_text5",
    #         refresh_on_update=True,
    #         override_height=75,
    #         debounce_time=0)
    #     if show:
    #         st.caption(text_to_be_copied)

    # with col4:
    #     text_to_be_copied = df.loc[df_new['publisher']=='IEEE ', 'statement'].values[0]
    #     copy_dict = {"content": text_to_be_copied}

    #     copy_button = Button(label="IEEE")
    #     copy_button.js_on_event("button_click", CustomJS(args=copy_dict, code="""
    #         navigator.clipboard.writeText(content);
    #         """))

    #     no_event = streamlit_bokeh_events(
    #         copy_button,
    #         events="GET_TEXT6",
    #         key="get_text6",
    #         refresh_on_update=True,
    #         override_height=75,
    #         debounce_time=0)
    #     if show:
    #         st.caption(text_to_be_copied)

    # col1, col2, col3, col4 = st.columns(4)

    # with col1:
    #     text_to_be_copied = df.loc[df_new['publisher']=='SAGE publications', 'statement'].values[0]
    #     copy_dict = {"content": text_to_be_copied}

    #     copy_button = Button(label="SAGE publications")
    #     copy_button.js_on_event("button_click", CustomJS(args=copy_dict, code="""
    #         navigator.clipboard.writeText(content);
    #         """))

    #     no_event = streamlit_bokeh_events(
    #         copy_button,
    #         events="GET_TEXT7",
    #         key="get_text7",
    #         refresh_on_update=True,
    #         override_height=75,
    #         debounce_time=0)
    #     if show:
    #         st.caption(text_to_be_copied)

    # with col2:
    #     text_to_be_copied = df.loc[df_new['publisher']=='BMJ Publishing', 'statement'].values[0]
    #     copy_dict = {"content": text_to_be_copied}

    #     copy_button = Button(label="BMJ Publishing")
    #     copy_button.js_on_event("button_click", CustomJS(args=copy_dict, code="""
    #         navigator.clipboard.writeText(content);
    #         """))

    #     no_event = streamlit_bokeh_events(
    #         copy_button,
    #         events="GET_TEXT8",
    #         key="get_text8",
    #         refresh_on_update=True,
    #         override_height=75,
    #         debounce_time=0)
    #     if show:
    #         st.caption(text_to_be_copied)

    # with col3:
    #     text_to_be_copied = df.loc[df_new['publisher']=='Oxford University Press (OUP)', 'statement'].values[0]
    #     copy_dict = {"content": text_to_be_copied}

    #     copy_button = Button(label="Oxford University Press (OUP)")
    #     copy_button.js_on_event("button_click", CustomJS(args=copy_dict, code="""
    #         navigator.clipboard.writeText(content);
    #         """))

    #     no_event = streamlit_bokeh_events(
    #         copy_button,
    #         events="GET_TEXT9",
    #         key="get_text9",
    #         refresh_on_update=True,
    #         override_height=75,
    #         debounce_time=0)
    #     if show:
    #         st.caption(text_to_be_copied)

    # with col4:
    #     text_to_be_copied = df.loc[df_new['publisher']=='American Chemical Society', 'statement'].values[0]
    #     copy_dict = {"content": text_to_be_copied}

    #     copy_button = Button(label="American Chemical Society")
    #     copy_button.js_on_event("button_click", CustomJS(args=copy_dict, code="""
    #         navigator.clipboard.writeText(content);
    #         """))

    #     no_event = streamlit_bokeh_events(
    #         copy_button,
    #         events="GET_TEXT10",
    #         key="get_text10",
    #         refresh_on_update=True,
    #         override_height=75,
    #         debounce_time=0)
    #     if show:
    #         st.caption(text_to_be_copied)

    # st.write('Creative Commons statements. Click on the button to copy the statement.')

    # col1, col2, col3 = st.columns(3)

    # with col1:
    #     text_to_be_copied = df.loc[df_new['publisher']=='CC BY licence', 'statement'].values[0]
    #     copy_dict = {"content": text_to_be_copied}

    #     copy_button = Button(label="CC BY")
    #     copy_button.js_on_event("button_click", CustomJS(args=copy_dict, code="""
    #         navigator.clipboard.writeText(content);
    #         """))

    #     no_event = streamlit_bokeh_events(
    #         copy_button,
    #         events="GET_TEXTccby",
    #         key="get_textccby",
    #         refresh_on_update=True,
    #         override_height=75,
    #         debounce_time=0)

    # with col2:
    #     text_to_be_copied = df.loc[df_new['publisher']=='CC BY-NC licence', 'statement'].values[0]
    #     copy_dict = {"content": text_to_be_copied}

    #     copy_button = Button(label="CC BY-NC")
    #     copy_button.js_on_event("button_click", CustomJS(args=copy_dict, code="""
    #         navigator.clipboard.writeText(content);
    #         """))

    #     no_event = streamlit_bokeh_events(
    #         copy_button,
    #         events="GET_TEXTccbync",
    #         key="get_textccbync",
    #         refresh_on_update=True,
    #         override_height=75,
    #         debounce_time=0)

    # with col3:
    #     text_to_be_copied = df.loc[df_new['publisher']=='CC BY-NC-ND licence', 'statement'].values[0]
    #     copy_dict = {"content": text_to_be_copied}

    #     copy_button = Button(label="CC BY-NC-ND")
    #     copy_button.js_on_event("button_click", CustomJS(args=copy_dict, code="""
    #         navigator.clipboard.writeText(content);
    #         """))

    #     no_event = streamlit_bokeh_events(
    #         copy_button,
    #         events="GET_TEXTccbyncnd",
    #         key="get_textccbyncnd",
    #         refresh_on_update=True,
    #         override_height=75,
    #         debounce_time=0)

    with st.expander('All publisher statements'):        
        st.write('This page lists all the copyright statements as a dataset. You can copy or download all the datasets. The dataset updated on 28 November 2022')
        st.dataframe(df_new)
        copy_button = Button(label="Copy data all copyright statements")
        copy_button.js_on_event("button_click", CustomJS(args=dict(df_new=df_new.to_csv(sep='\t')), code="""
            navigator.clipboard.writeText(df_new);
            """))

        no_event = streamlit_bokeh_events(
            copy_button,
            events="GET_TEXT11",
            key="get_text11",
            refresh_on_update=True,
            override_height=75,
            debounce_time=0)

        def convert_df(df):
            return df.to_csv(index=False).encode('cp1252') # not utf-8 because of the weird character,  Â

        csv = convert_df(df_new)

        st.download_button("Press to Download", csv, "copyright_statements.csv", "text/csv", key='download-csv')

with tab2:                
    st.subheader('Rights retention statement:')
    st.write("[Rights retention statement](https://www.coalition-s.org/resources/rights-retention-strategy/) allows authors to exercise the rights of their accepted manuscripts. Copy the statement below and paste into your submitted version.")
    st.info('**'+df_rrs.loc[df_rrs['publisher']=='Rights retention statement', 'statement'].values[0]+'**')
    
    text_to_be_copied = df.loc[df_rrs['publisher']=='Rights retention statement', 'statement'].values[0]
    copy_dict = {"content": text_to_be_copied}

    copy_button = Button(label="Copy to clipboard")
    copy_button.js_on_event("button_click", CustomJS(args=copy_dict, code="""
    navigator.clipboard.writeText(content);
    """))

    no_event = streamlit_bokeh_events(
    copy_button,
    events="GET_TEXTrrs",
    key="get_textrrs",
    refresh_on_update=True,
    override_height=75,
    debounce_time=0)
    
    
with tab3:
    st.subheader('Grey literature citation generator:')
    st.write('You can generate your citation for [grey literature](https://library.leeds.ac.uk/info/1110/resource_guides/7/grey_literature) items by filling the boxes below.')
    year = st.text_input('Enter year:', '')
    authors = st.text_input('Enter author(s) ( *Surname, First letter of name* ) :', '')
    title = st.text_input('Enter title:', '')
    type = st.selectbox('Select a type of publication: ', ('Report', 'Preprint', 'Working paper', 'Blog post'))
    institution = st.text_input('Enter institution:', '')
    handle = st.text_input('Publication handle:', '')
    citation = ('© ' + year + ' '+ authors +'. '+"'"+title+"'. "+ '('+type+ ": "+institution+')'+" "+handle)
    if st.button('Show citation'):
        st.write('**Citation** : ')
        st.info(citation)

        text_to_be_copied = citation
        copy_dict = {"content": text_to_be_copied}

        copy_button = Button(label="Copy to clipboard")
        copy_button.js_on_event("button_click", CustomJS(args=copy_dict, code="""
        navigator.clipboard.writeText(content);
        """))

        no_event = streamlit_bokeh_events(
        copy_button,
        events="GET_TEXTcite",
        key="get_textcite",
        refresh_on_update=True,
        override_height=75,
        debounce_time=0)   

with st.expander("Sherpa Romeo"):
    components.iframe("https://v2.sherpa.ac.uk/romeo/", height=1500)

with st.expander("Contact us"):
    contact_form = """
    <form action="https://formsubmit.co/yusufaliozkan37@gmail.com" method="POST">
         <input type="hidden" name="_captcha" value="false">
         <input type="text" name="name" placeholder="Your name" required>
         <input type="email" name="email" placeholder="Your email" required>
         <textarea name="message" placeholder="Your message here"></textarea>
         <button type="submit">Send</button>
    </form>
    """

    st.markdown(contact_form, unsafe_allow_html=True)

    # Use Local CSS File
    def local_css(file_name):
        with open(file_name) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    local_css("style.css")
