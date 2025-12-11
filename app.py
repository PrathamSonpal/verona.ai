# app.py — Verona AI (polished UI, stable session_state handling)
import os
import json
from datetime import datetime

import streamlit as st
from openai import OpenAI

# -----------------------------
# Verona AI — Polished UI
# Single-file Streamlit app (drop into Streamlit Cloud)
# -----------------------------

st.set_page_config(page_title="Verona AI", page_icon="🤖", layout="wide")


def now_ts():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def init_state():
    # Keep initial system message in messages[0]
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "system", "content": "You are Verona, a friendly, concise assistant.", "ts": now_ts()}
        ]
    if "uploaded_files" not in st.session_state:
        st.session_state.uploaded_files = []
    if "theme" not in st.session_state:
        st.session_state.theme = "light"


init_state()

# -----------------------------
# CSS (light + dark)
# -----------------------------
LIGHT_CSS = """
<style>
:root{
  --bg: #ffffff; --panel:#f7f7fb; --muted:#6b7280; --accent:#6c5ce7; --user:#DCF8C6; --assistant:#f1f0f0;
}
body{background:var(--bg)!important}
.header{display:flex;align-items:center;gap:12px}
.logo{font-size:28px}
.tagline{color:var(--muted);font-size:14px}
.chat-panel{display:flex;flex-direction:column;gap:8px;padding:12px}
.bubble{padding:12px 14px;border-radius:14px;max-width:78%;line-height:1.45}
.user{align-self:flex-end;background:var(--user)}
.assistant{align-self:flex-start;background:var(--assistant)}
.meta{font-size:12px;color:var(--muted);margin-bottom:6px}
.role-badge{font-weight:600;margin-right:8px}
.msg-row{display:flex;flex-direction:column}
.avatar{width:36px;height:36px;border-radius:8px;display:inline-flex;align-items:center;justify-content:center;margin-right:8px}
.msg-with-avatar{display:flex;align-items:flex-start;gap:8px}
.chat-controls{display:flex;gap:8px;margin-bottom:12px}
.chips{display:flex;flex-wrap:wrap;gap:8px}
.chip{background:#efefff;padding:8px 12px;border-radius:999px;cursor:pointer}
.small-muted{font-size:12px;color:var(--muted)}
.card{background:var(--panel);padding:12px;border-radius:10px}
</style>
"""

DARK_CSS = """
<style>
:root{
  --bg: #0b1020; --panel:#0f1724; --muted:#94a3b8; --accent:#7c3aed; --user:#08332f; --assistant:#0b1220;
  color-scheme: dark;
}
body{background:var(--bg)!important;color:#e6eef8}
.header{display:flex;align-items:center;gap:12px}
.logo{font-size:28px}
.tagline{color:var(--muted);font-size:14px}
.chat-panel{display:flex;flex-direction:column;gap:8px;padding:12px}
.bubble{padding:12px 14px;border-radius:14px;max-width:78%;line-height:1.45}
.user{align-self:flex-end;background:linear-gradient(180deg, #054e45, #08332f);color:#dff6f0}
.assistant{align-self:flex-start;background:linear-gradient(180deg,#0f1724,#0b1220);color:#e6eef8}
.meta{font-size:12px;color:var(--muted);margin-bottom:6px}
.role-badge{font-weight:600;margin-right:8px}
.msg-row{display:flex;flex-direction:column}
.avatar{width:36px;height:36px;border-radius:8px;display:inline-flex;align-items:center;justify-content:center;margin-right:8px}
.msg-with-avatar{display:flex;align-items:flex-start;gap:8px}
.chat-controls{display:flex;gap:8px;margin-bottom:12px}
.chips{display:flex;flex-wrap:wrap;gap:8px}
.chip{background:#15162a;padding:8px 12px;border-radius:999px;cursor:pointer}
.small-muted{font-size:12px;color:var(--muted)}
.card{background:var(--panel);padding:12px;border-radius:10px}
</style>
"""

st.markdown(DARK_CSS if st.session_state.theme == "dark" else LIGHT_CSS, unsafe_allow_html=True)

# -----------------------------
# Sidebar
# -----------------------------
with st.sidebar:
    st.markdown("<div class='header'><div class='logo'>🤖 Verona AI</div></div>", unsafe_allow_html=True)
    st.write("A compact, polished assistant UI. Use the controls below to manage the model and conversation.")

    st.markdown("---")
    HF_TOKEN = os.getenv("HF_TOKEN")
    if not HF_TOKEN:
        st.error("HF_TOKEN not set. Add it to Streamlit Cloud secrets or env vars.")

    st.subheader("Model")
    MODEL_ID = st.text_input("Model ID (router)", value="HuggingFaceTB/SmolLM3-3B:hf-inference")
    temperature = st.slider("Temperature", 0.0, 1.0, 0.2, 0.05)
    max_tokens = st.slider("Max tokens", 64, 2048, 512, 64)

    st.markdown("---")
    st.subheader("Conversation")
    if st.button("Clear conversation"):
        # keep original system prompt, clear rest
        orig_system = st.session_state.messages[0]["content"] if st.session_state.messages else "You are Verona, a friendly, concise assistant."
        st.session_state.messages = [{"role": "system", "content": orig_system, "ts": now_ts()}]
        st.success("Conversation cleared")

    if st.session_state.messages:
        st.download_button("Download conversation (.json)", json.dumps(st.session_state.messages, indent=2), file_name="verona_conversation.json")

    uploaded_conv = st.file_uploader("Import conversation (.json)", type=["json"])
    if uploaded_conv:
        try:
            parsed = json.load(uploaded_conv)
            # basic validation
            if isinstance(parsed, list):
                st.session_state.messages = parsed
                st.success("Conversation imported")
            else:
                st.error("Conversation file must be a JSON list of messages.")
        except Exception:
            st.error("Invalid conversation file")

    st.markdown("---")
    st.subheader("Quick prompts")
    ex1, ex2, ex3 = st.columns(3)
    if ex1.button("Summarize repo"):
        st.session_state.messages.append({"role": "user", "content": "Summarize this repo in two sentences.", "ts": now_ts()})
    if ex2.button("Email subject ideas"):
        st.session_state.messages.append({"role": "user", "content": "Generate 5 subject lines for an email about product launch.", "ts": now_ts()})
    if ex3.button("Explain TCP vs UDP"):
        st.session_state.messages.append({"role": "user", "content": "Explain the difference between TCP and UDP for a beginner.", "ts": now_ts()})

    st.markdown("---")
    st.subheader("System prompt")
    # Use a separate widget key for system prompt to avoid touching messages[...] direct widget-backed keys
    system_prompt = st.text_area("System instruction (first message)", value=st.session_state.messages[0]["content"], height=120, key="system_prompt_widget")
    # sync the widget value to messages[0] so that it's used in subsequent calls, without creating conflicts later
    st.session_state.messages[0]["content"] = system_prompt

    st.markdown("---")
    st.write("Theme")
    if st.button("Toggle dark/light"):
        st.session_state.theme = "dark" if st.session_state.theme == "light" else "light"
        st.experimental_rerun()

    st.markdown("---")
    st.caption("Verona AI — Polished UI. Built for clarity and speed.")

# -----------------------------
# Main layout: chat center + right panel
# -----------------------------
col_main, col_right = st.columns([3, 1])

with col_main:
    st.markdown(
        "<div style='display:flex;align-items:center;justify-content:space-between'><div><h2>Verona</h2><div class='tagline'>Smart, concise answers — now prettier.</div></div></div>",
        unsafe_allow_html=True,
    )

    # Chat panel (render messages)
    chat_box = st.container()
    with chat_box:
        for idx, msg in enumerate(st.session_state.messages):
            role = msg.get("role", "user")
            content = msg.get("content", "")
            ts = msg.get("ts", "")
            if not content:
                continue

            if role == "assistant":
                avatar = "🟣"
                role_label = "Verona"
                bubble_class = "assistant"
            elif role == "system":
                avatar = "⚙️"
                role_label = "System"
                bubble_class = "assistant"
            else:
                avatar = "🙂"
                role_label = "You"
                bubble_class = "user"

            st.markdown(
                f"<div class='msg-row'><div class='meta'><span class='role-badge'>{role_label}</span><span class='small-muted'>{ts}</span></div><div class='msg-with-avatar'><div class='avatar'>{avatar}</div><div class='bubble {bubble_class}'>{content}</div></div></div>",
                unsafe_allow_html=True,
            )

    # Input area wrapped in a form to avoid widget-state conflicts
    with st.form("input_form", clear_on_submit=False):
        prompt_text = st.text_area("Ask Verona anything...", height=120, key="prompt_input")
        send_col, reset_col = st.columns([1, 1])
        with send_col:
            send = st.form_submit_button("Send")
        with reset_col:
            reset = st.form_submit_button("Reset input (clear)")

        # Handle reset: remove the widget-backed key safely and rerun
        if reset:
            st.session_state.pop("prompt_input", None)
            # Clear the form field visually by rerunning the app
            st.experimental_rerun()

        # Handle send: append user message, call API, add assistant response
        if send:
            if not prompt_text or not prompt_text.strip():
                st.warning("Please type a message before sending.")
            else:
                # append user message
                st.session_state.messages.append({"role": "user", "content": prompt_text.strip(), "ts": now_ts()})

                # build api messages (use st.session_state.messages as-is)
                api_messages = []
                for m in st.session_state.messages:
                    api_messages.append({"role": m["role"], "content": m["content"]})

                # call model
                with st.spinner("Verona is thinking..."):
                    try:
                        if not HF_TOKEN:
                            raise ValueError("HF_TOKEN not configured in environment.")

                        client = OpenAI(base_url="https://router.huggingface.co/v1", api_key=HF_TOKEN)
                        response = client.chat.completions.create(
