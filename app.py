import os
import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="Verona AI", page_icon="🤖")
st.title("🤖 Verona AI")

# ✅ DEFINE TOKEN FIRST
HF_TOKEN = os.getenv("HF_TOKEN")

if not HF_TOKEN:
    st.error("HF_TOKEN not set. Please configure secrets.")
    st.stop()

# ✅ NOW SAFE TO USE
client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key=HF_TOKEN,
)

MODEL_ID = "HuggingFaceTB/SmolLM3-3B:hf-inference"

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Ask Verona anything..."):
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = client.chat.completions.create(
                model=MODEL_ID,
                messages=st.session_state.messages,
            )

            reply = response.choices[0].message.content
            if "<think>" in reply:
                reply = reply.split("</think>")[-1].strip()

        st.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})
