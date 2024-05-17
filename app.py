from openai import OpenAI
import streamlit as st
from prompts.system_prompts import SYSTEM_PROMPT_1_A
from audiorecorder import audiorecorder

st.title("Pensieve")

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-4o"

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": SYSTEM_PROMPT_1_A},
        {"role": "assistant", "content": "Tell me about your wedding day."},
    ]

for message in st.session_state.messages[1:]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("What is up?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        stream = client.chat.completions.create(
            model=st.session_state["openai_model"],
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            stream=True,
        )
        response = st.write_stream(stream)
    st.session_state.messages.append({"role": "assistant", "content": response})


with st.container():

    if st.button("Submit recording"):
        st.write("Recording submitted")

    audio = audiorecorder(
        start_prompt="",
        stop_prompt="",
        pause_prompt="",
        show_visualizer=True,
        key=None,
    )

    if len(audio) > 0:
        # To play audio in frontend:
        st.audio(audio.export().read())

        # To save audio to a file, use pydub export method:
        audio.export("audio.wav", format="wav")
