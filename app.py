import os
import json
import streamlit as st
from openai import OpenAI

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(page_title="Verona AI", page_icon="🤖")
st.title("🤖 Verona AI — Fast, Smart, and Friendly")
st.caption("Powered by Hugging Face Inference & Llama 3.2")

# -----------------------------
# TOKEN SETUP
# -----------------------------
HF_TOKEN = os.getenv("HF_TOKEN")

if not HF_TOKEN:
    st.error("HF_TOKEN not set. Please configure it in Streamlit Secrets.")
    st.stop()

client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key=HF_TOKEN,
)

MODEL_ID = "meta-llama/Llama-3.2-1B-Instruct:hf-inference"

# -----------------------------
# CHAT HISTORY SAVE/LOAD
# -----------------------------
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

# -----------------------------
# INITIALIZE SESSION
# -----------------------------
if "messages" not in st.session_state:
    load_history()

# -----------------------------
# DISPLAY CHAT HISTORY
# -----------------------------
for msg in st.session_state.messages:
    avatar = "🤖" if msg["role"] == "assistant" else "🙂"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

# -----------------------------
# USER INPUT
# -----------------------------
if prompt := st.chat_input("Ask Verona anything..."):

    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    save_history()

    with st.chat_message("user", avatar="🙂"):
        st.markdown(prompt)

    # -----------------------------
    # AI RESPONSE
    # -----------------------------
    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("Verona is thinking..."):
            try:
                system_instruction = {
                    "role": "system",
                    "content": (
                        "You are Verona, a friendly, highly accurate AI assistant. "
                        "Give helpful, concise answers. If users ask for detailed explanations, provide them calmly."
                    )
                }

                # Only send last 6 messages for speed
                conversation = [system_instruction] + st.session_state.messages[-6:]

                completion = client.chat.completions.create(
                    model=MODEL_ID,
                    messages=conversation,
                )

                reply = completion.choices[0].message.content

                # Remove <think> blocks if any
                if "<think>" in reply:
                    reply = reply.split("</think>")[-1].strip()

            except Exception as e:
                reply = f"❌ Error: {str(e)}"

        st.markdown(reply)

    # Add assistant message to history
    st.session_state.messages.append({"role": "assistant", "content": reply})
    save_history()
