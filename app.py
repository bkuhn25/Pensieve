from openai import OpenAI
import streamlit as st
from prompts.system_prompts import SYSTEM_PROMPT_1_A, SYSTEM_PROMPT_1_B
from audiorecorder import audiorecorder

st.title("Pensieve")

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

chat_container = st.container(border=True)

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-4o"

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": SYSTEM_PROMPT_1_B},
        {
            "role": "assistant",
            "content": "Tell me about your wedding day.",
        },
    ]
with chat_container:
    for message in st.session_state.messages[1:]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


audio = audiorecorder(
    start_prompt="",
    stop_prompt="",
    pause_prompt="",
    show_visualizer=True,
    key=None,
)

if len(audio) > 0:

    with chat_container:
        with st.spinner("Transcribing audio..."):
            # # To play audio in frontend:
            # st.audio(audio.export().read())

            # To save audio to a file
            audio.export("audio.wav", format="wav")
            # make request to whisper to transcribe the audio
            audio_file = open("audio.wav", "rb")
            transcript = client.audio.transcriptions.create(
                model="whisper-1", file=audio_file
            )
            prompt = transcript.text

    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with chat_container:
            with st.chat_message("user"):
                st.markdown(prompt)

        # use llm to generate response
        with chat_container:
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
