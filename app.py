import os
import json
import time
from datetime import datetime
import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="Verona AI", page_icon="🤖", layout="wide")

# -----------------------------
# Utilities
# -----------------------------

def now_ts():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def init_state():
    if "messages" not in st.session_state:
        # seed with friendly system message
        st.session_state.messages = [
            {"role": "system", "content": "You are Verona, a friendly, concise assistant.", "ts": now_ts()},
        ]
    if "pinned" not in st.session_state:
        st.session_state.pinned = []
    if "theme" not in st.session_state:
        st.session_state.theme = "light"
    if "uploaded_files" not in st.session_state:
        st.session_state.uploaded_files = []


init_state()

# -----------------------------
# Styling (light + dark)
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
# Sidebar (left) - controls and conversation list
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
        st.session_state.messages = [{"role": "system", "content": st.session_state.messages[0]["content"], "ts": now_ts()}]
        st.success("Conversation cleared")

    if st.session_state.messages and st.download_button("Download .json", json.dumps(st.session_state.messages, indent=2)):
        pass

    uploaded_conv = st.file_uploader("Import conversation (.json)", type=["json"])
    if uploaded_conv:
        try:
            parsed = json.load(uploaded_conv)
            st.session_state.messages = parsed
            st.success("Conversation imported")
        except Exception as e:
            st.error("Invalid conversation file")

    st.markdown("---")
    st.subheader("Quick prompts")
    example_row = st.container()
    ex1, ex2, ex3 = example_row.columns(3)
    if ex1.button("Summarize repo"):
        st.session_state.messages.append({"role": "user", "content": "Summarize this repo in two sentences.", "ts": now_ts()})
    if ex2.button("Email subject ideas"):
        st.session_state.messages.append({"role": "user", "content": "Generate 5 subject lines for an email about product launch.", "ts": now_ts()})
    if ex3.button("Explain TCP vs UDP"):
        st.session_state.messages.append({"role": "user", "content": "Explain the difference between TCP and UDP for a beginner.", "ts": now_ts()})

    st.markdown("---")
    st.subheader("System prompt")
    st.session_state.messages[0]["content"] = st.text_area("System instruction (first message)", value=st.session_state.messages[0]["content"], height=120)

    st.markdown("---")
    st.write("Theme")
    if st.button("Toggle dark/light"):
        st.session_state.theme = "dark" if st.session_state.theme == "light" else "light"
        st.experimental_rerun()

    st.markdown("---")
    st.caption("Verona AI — Polished UI. Built for clarity and speed.")

# -----------------------------
# Main layout: chat center + right panel for context
# -----------------------------
col_main, col_right = st.columns([3, 1])

with col_main:
    # Header
    st.markdown("<div style='display:flex;align-items:center;justify-content:space-between'><div><h2>Verona</h2><div class='tagline'>Smart, concise answers — now prettier.</div></div></div>", unsafe_allow_html=True)

    # Chat controls (chips)
    st.markdown("<div class='chat-controls'><div class='chips'></div></div>", unsafe_allow_html=True)

    # Chat panel
    chat_box = st.container()
    with chat_box:
        # render messages
        for idx, msg in enumerate(st.session_state.messages):
            role = msg.get("role", "user")
            content = msg.get("content", "")
            ts = msg.get("ts", "")

            # skip rendering empty
            if not content:
                continue

            # layout with avatar for assistant and user
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

            # show row
            st.markdown(f"<div class='msg-row'><div class='meta'><span class='role-badge'>{role_label}</span><span class='small-muted'>{ts}</span></div><div class='msg-with-avatar'><div class='avatar'>{avatar}</div><div class='bubble {bubble_class}'>{content}</div></div></div>", unsafe_allow_html=True)

    # Input area
    prompt = st.text_area("Ask Verona anything...", height=120, key="prompt_input")

    col_send, col_clear = st.columns([1, 1])
    with col_send:
        if st.button("Send"):
            if prompt.strip():
                st.session_state.messages.append({"role": "user", "content": prompt.strip(), "ts": now_ts()})
                st.session_state.prompt_input = ""

                # Prepare API messages
                api_messages = []
                for m in st.session_state.messages:
                    # openai router expects roles 'system'|'user'|'assistant'
                    api_messages.append({"role": m["role"], "content": m["content"]})

                # Call model
                with st.spinner("Verona is thinking..."):
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
                        if "</think>" in reply:
                            reply = reply.split("</think>")[-1].strip()

                        st.session_state.messages.append({"role": "assistant", "content": reply, "ts": now_ts()})
                        st.experimental_rerun()

                    except Exception as e:
                        st.error(f"Error calling model: {e}")
            else:
                st.warning("Please type a message before sending.")

    with col_clear:
        if st.button("Reset input"):
            st.session_state.prompt_input = ""

with col_right:
    st.subheader("Context & Files")
    st.write("Upload small files (txt, md). Verona can use them as context.")
    uploaded = st.file_uploader("Upload files", accept_multiple_files=True, type=["txt", "md", "json"])
    if uploaded:
        for up in uploaded:
            try:
                raw = up.read()
                # try decode safely
                try:
                    text = raw.decode("utf-8")
                except Exception:
                    text = str(raw)[:300]
                summary = text[:1000]
                item = {"name": up.name, "summary": summary, "full": text}
                # add if new
                if not any(f["name"] == up.name for f in st.session_state.uploaded_files):
                    st.session_state.uploaded_files.append(item)
            except Exception:
                st.warning(f"Couldn't read {up.name}")

    if st.session_state.uploaded_files:
        for f in st.session_state.uploaded_files:
            with st.expander(f['name']):
                st.code(f['summary'][:400] + ("..." if len(f['summary'])>400 else ""))
                if st.button(f"Include {f['name']} in next prompt", key=f"include_{f['name']}"):
                    # tack file summary onto system message for next call
                    st.session_state.messages[0]["content"] += f"\n\nContext file ({f['name']}):\n{f['summary']}"
                    st.success(f"Included {f['name']} as system context")

    st.markdown("---")
    st.subheader("Conversation tools")
    if st.button("Export conversation (.json)"):
        st.download_button("Download JSON", json.dumps(st.session_state.messages, indent=2), file_name="verona_convo.json")

    if st.button("Copy system prompt to clipboard"):
        st.write(st.session_state.messages[0]["content"])

# -----------------------------
# Footer: tips
# -----------------------------
st.markdown("---")
st.markdown("**Tips**: Keep system prompts short. Use temperature for creativity. Use the file uploader to provide reference docs.")

# EOF
