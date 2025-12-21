import os
import base64
import streamlit as st
from openai import OpenAI

# =============================================================================
# CONFIG
# =============================================================================
LOGO_PATH = "assets/Verona AI Logo.png"   # 1024x1024 recommended
MODEL_ID = "HuggingFaceTB/SmolLM3-3B:hf-inference"
TEMPERATURE = 0.7
MAX_TOKENS = 2048

st.set_page_config(
    page_title="Verona AI",
    page_icon=LOGO_PATH,
    layout="centered",
)

# =============================================================================
# UTILS
# =============================================================================
def b64_image(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

LOGO_B64 = b64_image(LOGO_PATH)

# =============================================================================
# GLOBAL CSS — REAL PRODUCT UI
# =============================================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

:root {
  --bg: #0b0c10;
  --surface: #111318;
  --card: rgba(255,255,255,0.06);
  --border: rgba(255,255,255,0.08);
  --text: #f9fafb;
  --muted: #9ca3af;
  --accent: linear-gradient(135deg, #6366f1, #a855f7);
  --radius: 18px;
}

html, body {
  background: var(--bg);
  color: var(--text);
  font-family: 'Inter', sans-serif;
}

#MainMenu, footer, header { display: none; }

.block-container {
  max-width: 820px;
  padding-top: 2.2rem;
  padding-bottom: 6.5rem;
}

/* SIDEBAR */
section[data-testid="stSidebar"] {
  background: var(--surface);
  border-right: 1px solid var(--border);
}

/* HEADER */
.app-title {
  font-size: 3rem;
  font-weight: 800;
  background: var(--accent);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  text-align: center;
}

.app-subtitle {
  text-align: center;
  color: var(--muted);
  margin-top: 0.3rem;
  margin-bottom: 2.8rem;
}

/* CHAT WRAPPER */
.chat-wrapper {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

/* MESSAGE BUBBLES */
.msg {
  max-width: 78%;
  padding: 16px 18px;
  border-radius: var(--radius);
  line-height: 1.55;
  font-size: 0.96rem;
}

.msg.user {
  align-self: flex-end;
  background: var(--accent);
  color: white;
}

.msg.assistant {
  align-self: flex-start;
  background: var(--card);
  border: 1px solid var(--border);
  backdrop-filter: blur(14px);
}

/* INPUT */
.stChatInput {
  position: fixed;
  bottom: 1.5rem;
  left: 50%;
  transform: translateX(-50%);
  width: min(820px, 95%);
}

textarea {
  background: var(--surface) !important;
  color: var(--text) !important;
  border-radius: 16px !important;
  border: 1px solid var(--border) !important;
  padding: 14px !important;
}
</style>
""", unsafe_allow_html=True)

# =============================================================================
# CLIENT
# =============================================================================
HF_TOKEN = os.getenv("HF_TOKEN")
if not HF_TOKEN:
    st.error("HF_TOKEN missing")
    st.stop()

client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key=HF_TOKEN,
)

# =============================================================================
# STATE
# =============================================================================
if "messages" not in st.session_state:
    st.session_state.messages = []

# =============================================================================
# SIDEBAR
# =============================================================================
with st.sidebar:
    st.markdown(
        f"""
        <div style="display:flex;justify-content:center;margin-top:10px;">
          <img src="data:image/png;base64,{LOGO_B64}" width="64"/>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.markdown("### Verona AI")
    st.caption("Private • Intelligent • Fast")

    st.divider()

    if st.button("➕ New chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.divider()
    st.caption("Powered by Hugging Face")

# =============================================================================
# HEADER
# =============================================================================
st.markdown('<div class="app-title">Verona AI</div>', unsafe_allow_html=True)

if not st.session_state.messages:
    st.markdown(
        '<div class="app-subtitle">What would you like to work on?</div>',
        unsafe_allow_html=True
    )

# =============================================================================
# CHAT HISTORY (CUSTOM, NOT STREAMLIT)
# =============================================================================
st.markdown('<div class="chat-wrapper">', unsafe_allow_html=True)

for msg in st.session_state.messages:
    role = msg["role"]
    cls = "user" if role == "user" else "assistant"
    st.markdown(
        f'<div class="msg {cls}">{msg["content"]}</div>',
        unsafe_allow_html=True
    )

st.markdown('</div>', unsafe_allow_html=True)

# =============================================================================
# INPUT + STREAMING
# =============================================================================
if prompt := st.chat_input("Message Verona…"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.rerun()

# Stream last assistant reply
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    placeholder = st.empty()
    full = ""

    stream = client.chat.completions.create(
        model=MODEL_ID,
        messages=st.session_state.messages,
        temperature=TEMPERATURE,
        max_tokens=MAX_TOKENS,
        stream=True,
    )

    for chunk in stream:
        delta = chunk.choices[0].delta.content
        if not delta:
            continue

        full += delta

        if "<think>" in full and "</think>" not in full:
            placeholder.markdown(
                '<div class="msg assistant">Thinking…</div>',
                unsafe_allow_html=True
            )
        else:
            clean = full.split("</think>")[-1]
            placeholder.markdown(
                f'<div class="msg assistant">{clean}</div>',
                unsafe_allow_html=True
            )

    final = full.split("</think>")[-1].strip()
    st.session_state.messages.append({"role": "assistant", "content": final})
    st.rerun()
