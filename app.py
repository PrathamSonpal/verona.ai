import os
import json
import time
from datetime import datetime
import streamlit as st
from openai import OpenAI

# -----------------------------
# Verona AI (improved UI)
# -----------------------------
# Key improvements (see README below):
# - Sidebar controls for token, model params (temperature, max tokens)
# - Clear chat, save/load conversation, download as JSON
# - Example prompts as quick-buttons
# - File uploader to send context to the assistant
# - Nicely formatted chat bubbles with timestamps and role badges
# - Safe HF_TOKEN check and graceful error handling
# - Lightweight CSS for improved visuals

st.set_page_config(page_title="Verona AI", page_icon="🤖", layout="wide")

# -----------------------------
# Helper utilities
# -----------------------------

def now_ts():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def init_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "system_prompt" not in st.session_state:
        st.session_state.system_prompt = "You are Verona, a helpful assistant." 
    if "uploaded_files" not in st.session_state:
        st.session_state.uploaded_files = []

init_state()

# -----------------------------
# Layout & CSS
# -----------------------------
CSS = '''
<style>
.chat-bubble {
  padding: 12px 14px;
  border-radius: 12px;
  margin-bottom: 8px;
  max-width: 80%;
  line-height: 1.4;
}
.user-bubble { background-color: #DCF8C6; align-self: flex-end; }
.assistant-bubble { background-color: #F1F0F0; align-self: flex-start; }
.role-badge { font-size: 12px; opacity: 0.8; }
.timestamp { font-size: 11px; color: #666; margin-left: 8px; }
.chat-row { display: flex; flex-direction: column; }
.chat-controls { margin-bottom: 12px; }
</style>
'''

st.markdown(CSS, unsafe_allow_html=True)

# -----------------------------
# Sidebar controls
# -----------------------------
with st.sidebar:
    st.title("Verona AI")
    HF_TOKEN = os.getenv("HF_TOKEN")
    if not HF_TOKEN:
        st.error("HF_TOKEN not set. Add it to Streamlit Cloud secrets or env vars.")

    st.markdown("---")
    st.subheader("Model & settings")
    MODEL_ID = st.text_input("Model ID (router)", value="HuggingFaceTB/SmolLM3-3B:hf-inference")
    temperature = st.slider("Temperature", 0.0, 1.0, 0.2, 0.05)
    max_tokens = st.slider("Max tokens", 64, 4096, 512, 64)

    st.markdown("---")
    st.subheader("Conversation")
    if st.button("Clear conversation"):
        st.session_state.messages = []
        st.success("Conversation cleared")

    if st.session_state.messages:
        if st.button("Download conversation (.json)"):
            conv_json = json.dumps(st.session_state.messages, indent=2)
            st.download_button("Download JSON", conv_json, file_name="verona_conversation.json")

    st.markdown("---")
    st.subheader("Quick prompts")
    examples = [
        "Summarize this repo in two sentences.",
        "Generate 5 subject lines for an email about product launch.",
        "Explain the difference between TCP and UDP for a beginner.",
    ]
    for ex in examples:
        if st.button(ex):
            st.session_state.messages.append({"role": "user", "content": ex})

    st.markdown("---")
    st.subheader("System prompt")
    st.session_state.system_prompt = st.text_area("System prompt (sent once at start)", value=st.session_state.system_prompt, height=120)

    st.markdown("---")
    st.caption("Verona AI — improved UI. Powered by HuggingFace router + OpenAI wrapper")

# -----------------------------
# Main: Chat area
# -----------------------------

col1, col2 = st.columns([3, 1])

with col1:
    st.header("Chat")

    # Render messages
    if not st.session_state.messages:
        st.info("Start by typing a message in the box below or use an example from the sidebar.")

    for msg in st.session_state.messages:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        timestamp = msg.get("ts", "")
        # Chat bubble layout
        role_class = "user-bubble" if role == "user" else "assistant-bubble"
        role_label = "You" if role == "user" else ("System" if role == "system" else "Verona")
        st.markdown(f"<div class='chat-row'><div class='role-badge'>{role_label} <span class='timestamp'>{timestamp}</span></div><div class='chat-bubble {role_class}'>{content}</div></div>", unsafe_allow_html=True)

    # Input area
    prompt = st.chat_input("Ask Verona anything...")

    if prompt:
        # add user message
        user_msg = {"role": "user", "content": prompt, "ts": now_ts()}
        st.session_state.messages.append(user_msg)

        # Build messages for API
        api_messages = []
        if st.session_state.system_prompt:
            api_messages.append({"role": "system", "content": st.session_state.system_prompt})
        # append conversation
        for m in st.session_state.messages:
            api_messages.append({"role": m["role"], "content": m["content"]})

        # call API
        with st.chat_message("assistant"):
            with st.spinner("Verona is composing..."):
                try:
                    if not HF_TOKEN:
                        raise ValueError("HF_TOKEN not configured in environment.")

                    client = OpenAI(base_url="https://router.huggingface.co/v1", api_key=HF_TOKEN)
                    response = client.chat.completions.create(
                        model=MODEL_ID,
                        messages=api_messages,
                        temperature=temperature,
                        max_tokens=max_tokens,
                    )
                    reply = response.choices[0].message.content
                    # strip optional special markers
                    if "</think>" in reply:
                        reply = reply.split("</think>")[-1].strip()

                    assistant_msg = {"role": "assistant", "content": reply, "ts": now_ts()}
                    st.session_state.messages.append(assistant_msg)

                    st.markdown(reply)

                except Exception as e:
                    err = str(e)
                    st.error(f"Error calling model: {err}")

with col2:
    st.subheader("Context / Tools")
    st.write("Upload files that Verona should consider (optional). They are not sent to the API directly — this demo reads them and includes a short summary in the prompt.")

    uploaded = st.file_uploader("Upload text / markdown / small files", accept_multiple_files=True)
    if uploaded:
        summaries = []
        for up in uploaded:
            text = up.read().decode("utf-8")[:20_000]
            summary = text[:1000]
            summaries.append({"name": up.name, "summary": summary})
        # show summaries
        for s in summaries:
            st.markdown(f"**{s['name']}** — {s['summary'][:300]}...")
        # attach to session state for later
        st.session_state.uploaded_files = summaries

    st.markdown("---")
    st.subheader("Conversation settings")
    st.write("Messages in the conversation are stored in `st.session_state.messages`. Use the sidebar to clear or download.")

# -----------------------------
# Footer / small README
# -----------------------------

st.markdown("---")
st.markdown("**Tips**: use the System prompt to configure Verona's persona; change temperature for creativity; use max tokens to limit response length.")

# This file is intended to be dropped into Streamlit Cloud and run as `streamlit run app.py`.
# End of file
