import os
import json
import streamlit as st
from openai import OpenAI

# ---------------------------------
# PAGE CONFIG
# ---------------------------------
st.set_page_config(page_title="Verona AI", page_icon="🤖")
st.title("🤖 Verona AI — Free & Smart")
st.caption("Using Hugging Face SmolLM2 1.7B Instruct (free)")

# ---------------------------------
# TOKEN SETUP
# ---------------------------------
HF_TOKEN = os.getenv("HF_TOKEN")

if not HF_TOKEN:
    st.error("HF_TOKEN not set. Please configure it in Streamlit Secrets.")
    st.stop()

client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key=HF_TOKEN,
)

# Supported free model
MODEL_ID = "HuggingFaceTB/SmolLM2-1.7B-Instruct:hf-inference"

# ---------------------------------
# CLEAN RESPONSE
# ---------------------------------
def clean_response(text):
    if "<think>" in text:
        text = text.split("</think>")[-1].strip()
    text = text.replace("<think>", "").replace("</think>", "")
    return text

# ---------------------------------
# SAVE/LOAD CHAT HISTORY
# ---------------------------------
def save_history():
    try:
        with open("history.json", "w") as f:
            json.dump(st.session_state.messages, f)
    except:
        pass

def load_history():
    try:
        with open("history.json", "r") as f:
            st.session_state.messages = json.load(f)
    except:
        st.session_state.messages = []

# ---------------------------------
# INITIALIZE SESSION
# ---------------------------------
if "messages" not in st.session_state:
    load_history()

# ---------------------------------
# DISPLAY CHAT HISTORY
# ---------------------------------
for msg in st.session_state.messages:
    avatar = "🤖" if msg["role"] == "assistant" else "🙂"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

# ---------------------------------
# USER INPUT
# ---------------------------------
if prompt := st.chat_input("Ask Verona anything..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    save_history()

    with st.chat_message("user", avatar="🙂"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("Verona is thinking..."):
            try:
                system_instruction = {
                    "role": "system",
                    "content": (
                        "You are Verona, a smart AI assistant. "
                        "Provide accurate and helpful answers. "
                        "Think before answering, but never reveal internal reasoning."
                    )
                }

                conversation = [system_instruction] + st.session_state.messages[-8:]

                completion = client.chat.completions.create(
                    model=MODEL_ID,
                    messages=conversation,
                )

                reply = completion.choices[0].message.content
                reply = clean_response(reply)

            except Exception as e:
                reply = f"❌ Error: {str(e)}"

        st.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})
    save_history()
