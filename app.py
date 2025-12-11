import os
import json
import streamlit as st
from openai import OpenAI

# ---------------------------------
# PAGE CONFIG
# ---------------------------------
st.set_page_config(page_title="Verona AI", page_icon="🤖")
st.title("🤖 Verona AI — Smarter, Cleaner, Faster")
st.caption("Powered by Hugging Face Inference — SmolLM3 1.7B Instruct")

# ---------------------------------
# TOKEN SETUP
# ---------------------------------
HF_TOKEN = os.getenv("HF_TOKEN")

if not HF_TOKEN:
    st.error("HF_TOKEN not set in Streamlit Secrets.")
    st.stop()

client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key=HF_TOKEN,
)

# BEST FREE SMART MODEL
MODEL_ID = "HuggingFaceTB/SmolLM3-1.7B-Instruct:hf-inference"


# ---------------------------------
# CLEAN THINK BLOCKS
# ---------------------------------
def clean_response(text):
    """Remove hidden <think> reasoning to keep answers clean."""
    if "<think>" in text:
        text = text.split("</think>")[-1].strip()
    text = text.replace("<think>", "").replace("</think>", "")
    return text


# ---------------------------------
# CHAT HISTORY SAVE/LOAD
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

    # Store user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    save_history()

    with st.chat_message("user", avatar="🙂"):
        st.markdown(prompt)

    # ---------------------------------
    # AI RESPONSE
    # ---------------------------------
    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("Verona is thinking..."):

            try:
                # SMARTER SYSTEM PROMPT
                system_instruction = {
                    "role": "system",
                    "content": (
                        "You are Verona, a highly intelligent AI assistant. "
                        "Think deeply before answering. Provide accurate, structured, and thoughtful explanations. "
                        "Be friendly but professional. "
                        "NEVER reveal chain-of-thought, internal reasoning, or <think> blocks. "
                        "If a user asks for reasoning, give a short explanation instead of detailed chain-of-thought."
                    )
                }

                # Use last 8 messages to improve reasoning
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

    # Save assistant response
    st.session_state.messages.append({"role": "assistant", "content": reply})
    save_history()
