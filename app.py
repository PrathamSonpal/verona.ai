# app.py — Verona AI (cleaner UI, no temperature/tokens sliders)
import os
import json
from datetime import datetime

import streamlit as st
from openai import OpenAI

# -----------------------------
# Verona AI — Clean, friendly UI
# Single-file Streamlit app (drop into Streamlit Cloud)
# -----------------------------

st.set_page_config(page_title="Verona AI", page_icon="🤖", layout="wide")

# sensible fixed defaults (no sliders in UI)
DEFAULT_TEMPERATURE = 0.2
DEFAULT_MAX_TOKENS = 512

def now_ts():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def init_state():
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
# Styling (simple, friendly)
# -----------------------------
LIGHT_CSS = """
<style>
:root{
  --bg: #ffffff; --panel:#f7f7fb; --muted:#6b7280; --accent:#6c5ce7; --user:#DCF8C6; --assistant:#f1f0f0;
  --accent-strong: #6c5ce7;
}
body{background:var(--bg)!important}
.header{display:flex;align-items:center;gap:12px}
.logo{font-size:26px;font-weight:700}
.tagline{color:var(--muted);font-size:13px}
.container{padding:12px}
.bubble{padding:12px 14px;border-radius:12px;max-width:78%;line-height:1.45;white-space:pre-wrap}
.user{align-self:flex-end;background:var(--user)}
.assistant{align-self:flex-start;background:var(--assistant)}
.meta{font-size:12px;color:var(--muted);margin-bottom:6px}
.role-badge{font-weight:700;margin-right:8px}
.msg-row{display:flex;flex-direction:column;margin-bottom:10px}
.avatar{width:36px;height:36px;border-radius:8px;display:inline-flex;align-items:center;justify-content:center;margin-right:8px;font-weight:700}
.msg-with-avatar{display:flex;align-items:flex-start;gap:8px}
.controls{display:flex;gap:8px;margin-bottom:12px;align-items:center}
.quick-btn{background:transparent;border:1px solid #eee;padding:8px 12px;border-radius:999px;cursor:pointer}
.card{background:var(--panel);padding:12px;border-radius:10px}
.send-row{display:flex;gap:8px;align-items:center}
.send-btn{background:var(--accent-strong);color:white;padding:10px 18px;border-radius:8px;border:none;cursor:pointer;font-weight:700}
.small-muted{font-size:12px;color:var(--muted)}
</style>
"""

DARK_CSS = """
<style>
:root{
  --bg: #0b1020; --panel:#0f1724; --muted:#94a3b8; --accent:#7c3aed; --user:#08332f; --assistant:#0b1220;
  --accent-strong: #7c3aed;
  color-scheme: dark;
}
body{background:var(--bg)!important;color:#e6eef8}
.header{display:flex;align-items:center;gap:12px}
.logo{font-size:26px;font-weight:700}
.tagline{color:var(--muted);font-size:13px}
.container{padding:12px}
.bubble{padding:12px 14px;border-radius:12px;max-width:78%;line-height:1.45;white-space:pre-wrap}
.user{align-self:flex-end;background:linear-gradient(180deg,#075b4e,#08332f);color:#dff6f0}
.assistant{align-self:flex-start;background:linear-gradient(180deg,#0f1724,#0b1220);color:#e6eef8}
.meta{font-size:12px;color:var(--muted);margin-bottom:6px}
.role-badge{font-weight:700;margin-right:8px}
.msg-row{display:flex;flex-direction:column;margin-bottom:10px}
.avatar{width:36px;height:36px;border-radius:8px;display:inline-flex;align-items:center;justify-content:center;margin-right:8px;font-weight:700}
.msg-with-avatar{display:flex;align-items:flex-start;gap:8px}
.controls{display:flex;gap:8px;margin-bottom:12px;align-items:center}
.quick-btn{background:transparent;border:1px solid #1f2937;padding:8px 12px;border-radius:999px;cursor:pointer}
.card{background:var(--panel);padding:12px;border-radius:10px}
.send-row{display:flex;gap:8px;align-items:center}
.send-btn{background:var(--accent-strong);color:white;padding:10px 18px;border-radius:8px;border:none;cursor:pointer;font-weight:700}
.small-muted{font-size:12px;color:var(--muted)}
</style>
"""

st.markdown(DARK_CSS if st.session_state.theme == "dark" else LIGHT_CSS, unsafe_allow_html=True)

# -----------------------------
# Sidebar (simplified)
# -----------------------------
with st.sidebar:
    st.markdown("<div class='header'><div class='logo'>🤖 Verona</div></div>", unsafe_allow_html=True)
    st.markdown("<div class='tagline'>Smart, concise answers — friendly UI.</div>", unsafe_allow_html=True)

    st.markdown("---")
    HF_TOKEN = os.getenv("HF_TOKEN")
    if not HF_TOKEN:
        st.error("HF_TOKEN not set. Add it to Streamlit Cloud secrets or env vars.")

    st.subheader("Model")
    MODEL_ID = st.text_input("Model ID (router)", value="HuggingFaceTB/SmolLM3-3B:hf-inference")

    st.markdown("---")
    st.subheader("Conversation")
    if st.button("Clear conversation"):
        orig = st.session_state.messages[0]["content"] if st.session_state.messages else "You are Verona, a friendly, concise assistant."
        st.session_state.messages = [{"role": "system", "content": orig, "ts": now_ts()}]
        st.success("Conversation cleared")

    if st.session_state.messages:
        st.download_button("Download conversation", json.dumps(st.session_state.messages, indent=2), file_name="verona_conversation.json")

    uploaded_conv = st.file_uploader("Import conversation (.json)", type=["json"])
    if uploaded_conv:
        try:
            parsed = json.load(uploaded_conv)
            if isinstance(parsed, list):
                st.session_state.messages = parsed
                st.success("Conversation imported")
            else:
                st.error("JSON must be a list of messages.")
        except Exception:
            st.error("Invalid conversation file")

    st.markdown("---")
    st.subheader("System prompt")
    system_prompt = st.text_area("System message (guides Verona)", value=st.session_state.messages[0]["content"], height=120, key="system_prompt_widget")
    st.session_state.messages[0]["content"] = system_prompt

    st.markdown("---")
    st.write("Theme")
    if st.button("Toggle dark/light"):
        st.session_state.theme = "dark" if st.session_state.theme == "light" else "light"
        st.experimental_rerun()

    st.markdown("---")
    st.caption("No advanced knobs — simple defaults for a better UX.")

# -----------------------------
# Main layout: chat + context
# -----------------------------
col_main, col_right = st.columns([3, 1])

with col_main:
    st.markdown("<div style='display:flex;align-items:center;justify-content:space-between'><div><h2>Verona</h2><div class='tagline'>Quick, helpful answers — no clutter.</div></div></div>", unsafe_allow_html=True)

    # Friendly quick prompts row
    st.markdown("<div class='controls'>", unsafe_allow_html=True)
    quick_cols = st.columns(4)
    quick_texts = [
        "Summarize this repo in two sentences.",
        "Give 5 email subject lines for a product launch.",
        "Explain TCP vs UDP for a beginner.",
        "Make a short checklist for code review."
    ]
    for c, text in zip(quick_cols, quick_texts):
        if c.button(text, key=f"quick_{text[:12]}"):
            st.session_state.messages.append({"role": "user", "content": text, "ts": now_ts()})
    st.markdown("</div>", unsafe_allow_html=True)

    # Chat panel
    chat_box = st.container()
    with chat_box:
        for msg in st.session_state.messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            ts = msg.get("ts", "")
            if not content:
                continue

            if role == "assistant":
                avatar = "🟣"
                label = "Verona"
                cls = "assistant"
            elif role == "system":
                avatar = "⚙️"
                label = "System"
                cls = "assistant"
            else:
                avatar = "🙂"
                label = "You"
                cls = "user"

            st.markdown(
                f"<div class='msg-row'><div class='meta'><span class='role-badge'>{label}</span> <span class='small-muted'>{ts}</span></div>"
                f"<div class='msg-with-avatar'><div class='avatar'>{avatar}</div><div class='bubble {cls}'>{content}</div></div></div>",
                unsafe_allow_html=True,
            )

    # Input: simplified form with big send button
    with st.form("input_form", clear_on_submit=False):
        prompt_text = st.text_area("Ask Verona anything...", height=110, key="prompt_input", placeholder="Type your question, then click Send")
        send_col, reset_col = st.columns([1, 0.5])
        with send_col:
            send = st.form_submit_button("Send", help="Send message to Verona")
        with reset_col:
            reset = st.form_submit_button("Clear", help="Clear the input")

        if reset:
            st.session_state.pop("prompt_input", None)
            st.experimental_rerun()

        if send:
            if not prompt_text or not prompt_text.strip():
                st.warning("Please type a message before sending.")
            else:
                # append user message
                st.session_state.messages.append({"role": "user", "content": prompt_text.strip(), "ts": now_ts()})

                # prepare messages for API
                api_messages = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]

                # call model
                with st.spinner("Verona is thinking..."):
                    try:
                        if not HF_TOKEN:
                            raise ValueError("HF_TOKEN not configured in environment.")

                        client = OpenAI(base_url="https://router.huggingface.co/v1", api_key=HF_TOKEN)

                        response = client.chat.completions.create(
                            model=MODEL_ID,
                            messages=api_messages,
                            temperature=DEFAULT_TEMPERATURE,
                            max_tokens=DEFAULT_MAX_TOKENS
                        )

                        reply = response.choices[0].message.content
                        if "</think>" in reply:
                            reply = reply.split("</think>")[-1].strip()

                        st.session_state.messages.append({"role": "assistant", "content": reply, "ts": now_ts()})

                        # clear prompt and refresh UI
                        st.session_state.pop("prompt_input", None)
                        st.experimental_rerun()

                    except Exception as e:
                        st.error(f"Error calling model: {e}")

with col_right:
    st.subheader("Context & Files")
    st.write("Upload small files (txt, md). Use the button to include a file summary in the system prompt.")

    uploaded = st.file_uploader("Upload files", accept_multiple_files=True, type=["txt", "md", "json"])
    if uploaded:
        for up in uploaded:
            try:
                raw = up.read()
                try:
                    text = raw.decode("utf-8")
                except Exception:
                    text = str(raw)[:300]
                summary = text[:1000]
                item = {"name": up.name, "summary": summary, "full": text}
                if not any(f["name"] == up.name for f in st.session_state.uploaded_files):
                    st.session_state.uploaded_files.append(item)
            except Exception:
                st.warning(f"Couldn't read {up.name}")

    if st.session_state.uploaded_files:
        for f in st.session_state.uploaded_files:
            with st.expander(f["name"]):
                st.code(f["summary"][:400] + ("..." if len(f["summary"]) > 400 else ""))
                if st.button(f"Include {f['name']} in system prompt", key=f"include_{f['name']}"):
                    st.session_state.messages[0]["content"] += f"\n\nContext file ({f['name']}):\n{f['summary']}"
                    st.success(f"Included {f['name']} as system context")

    st.markdown("---")
    st.subheader("Tools")
    if st.button("Export conversation"):
        st.download_button("Download JSON", json.dumps(st.session_state.messages, indent=2), file_name="verona_convo.json")

    if st.button("Copy system prompt"):
        st.write(st.session_state.messages[0]["content"])

st.markdown("---")
st.markdown("**Tips**: Verona uses sensible defaults so you can focus on asking great questions.")
