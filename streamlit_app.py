import streamlit as st
from openai import OpenAI, APIStatusError
import os
from pydub import AudioSegment

st.set_page_config(
    page_title="Audio -> Text",
    page_icon="🎧",
)
st.title('🎧 Audio -> Text')
st.caption('Upload an mp3 file and get the text from it!') 


open_api_key = st.sidebar.text_input(
    "Enter Your OpenAI API Key 🗝️",
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
            try:
                transcription = client.audio.transcriptions.create(
                    model="whisper-1", 
                    file=audio_file
                )
                transcription_text = transcription.text
            except APIStatusError as e:
                if e.status_code == 413:
                    st.warning(f"File is bigger than 26214400 bytes - breaking mp3 into 2 files and trying again...")
                    with open("audio_file.mp3", "wb") as f:
                        f.write(audio_file.getbuffer())
                    sound = AudioSegment.from_mp3("audio_file.mp3")
                    halfway_point = len(sound) / 2
                    first_half = sound[:halfway_point]
                    second_half = sound[halfway_point:]
                    first_half.export("first_half.mp3", format="mp3")
                    second_half.export("second_half.mp3", format="mp3")

                    try:
                        with st.spinner('Transcribing first half...'):
                            with open("first_half.mp3", "rb") as f:
                                transcription_first_half = client.audio.transcriptions.create(
                                    model="whisper-1", 
                                    file=f
                                )
                        with st.spinner('Transcribing second half...'):
                            with open("second_half.mp3", "rb") as f:
                                transcription_second_half = client.audio.transcriptions.create(
                                    model="whisper-1", 
                                    file=f
                                )
                        transcription_text = transcription_first_half.text + transcription_second_half.text
                    except APIStatusError as e:
                        st.error(f"⚠️ {e}")

        st.write(f'**Text**: {transcription_text}')