from openai import OpenAI
import streamlit as st
from prompts.system_prompts import SYSTEM_PROMPT_1_A

st.title("Pensieve")

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# TODO - can provide the topic and let the llm come up with the initial question to the person

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Tell me about your wedding day."}
    ]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("What is up?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # compile messages for llm
        messages_for_llm = [
            {"role": m["role"], "content": m["content"]}
            for m in st.session_state.messages
        ]

        # add system prompt to beginning of messages list
        messages_for_llm.insert(0, {"role": "system", "content": SYSTEM_PROMPT_1_A})

        stream = client.chat.completions.create(
            model=st.session_state["openai_model"],
            messages=messages_for_llm,
            stream=True,
        )
        response = st.write_stream(stream)
    st.session_state.messages.append({"role": "assistant", "content": response})
