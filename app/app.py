import streamlit as st

st.title('A.I. Generated Video Game Music')

volume = st.slider('Volume', 0, 100)
speed = st.slider('Speed', 0, 100)
certainty = st.slider('Certainty', 0, 100)

audio_file = open('./audio/test.mp3', 'rb')
audio_bytes = audio_file.read()

st.audio(audio_bytes, format='audio/mp3')