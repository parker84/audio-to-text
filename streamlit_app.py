import streamlit as st
from openai import OpenAI
import os

st.set_page_config(
    page_title="Audio -> Text",
    page_icon="🎧",
)
st.title('🎧 Audio -> Text')
st.caption('Upload an mp3 file and get the text from it!') 


st.sidebar.subheader("Enter Your API Key 🗝️")
open_api_key = st.sidebar.text_input(
    "Open API Key", 
    value=st.session_state.get('open_api_key', ''),
    help="Get your API key from https://openai.com/",
    type='password'
)
os.environ["OPENAI_API_KEY"] = open_api_key
st.session_state['open_api_key'] = open_api_key

audio_file = st.file_uploader("Choose an mp3 file", type="mp3")

if audio_file is not None:
    st.audio(audio_file, format='audio/mp3')

    if open_api_key == '' or open_api_key is None:
        st.error("⚠️ Please enter your API key in the sidebar")
    else:
        with st.spinner('Transcribing...'):
            client = OpenAI(
                api_key=open_api_key
            )
            transcription = client.audio.transcriptions.create(
                model="whisper-1", 
                file=audio_file
            )
        st.write(f'**Text**: {transcription.text}')