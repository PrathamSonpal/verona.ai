import os
import base64
import streamlit as st
from openai import OpenAI

# -----------------------------------------------------------------------------
# 1. PAGE CONFIGURATION
# -----------------------------------------------------------------------------
LOGO_PATH = "assets/Verona AI Logo.png"   # use HIGH-RES (512x512+)
FAVICON_PATH = LOGO_PATH

st.set_page_config(
    page_title="Verona AI",
    page_icon=FAVICON_PATH,
    layout="centered",
)

# -----------------------------------------------------------------------------
# 2. UTILS
# -----------------------------------------------------------------------------
def load_logo_base64(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

LOGO_BASE64 = load_logo_base64(LOGO_PATH)

# -----------------------------------------------------------------------------
# 3. PREMIUM GLOBAL STYLING
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    :root {
        --bg: #ffffff;
        --surface: #f9fafb;
        --assistant: #f3f4f6;
        --text: #111827;
        --muted: #6b7280;
        --radius: 18px;
        --shadow: 0 12px 32px rgba(0,0,0,0.06);
        --gradient: linear-gradient(135deg, #4F46E5, #9333EA);
    }

    #MainMenu, footer, header { visibility: hidden; }

    body {
        background-color: var(--bg);
        color: var(--text);
        font-family: Inter, system-ui, sans-serif;
    }

    .block-container {
        max-width: 760px;
        padding-top: 2.8rem;
        padding-bottom: 7rem;
    }

    /* Title */
    .title-text {
        font-size: 3.2rem;
        font-weight: 800;
        text-align: center;
        background: var(--gradient);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.4rem;
    }

    .subtitle-text {
        text-align: center;
        color: var(--muted);
        font-size: 1.05rem;
        margin-bottom: 3rem;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: var(--surface);
        border-right: 1px solid #e5e7eb;
        padding-top: 1.8rem;
    }

    /* Chat message containers */
    .stChatMessage {
        border-radius: var(--radius);
        padding: 0.2rem;
        margin-bottom: 1rem;
    }

    /* User message */
    .stChatMessage[data-testid="chat-message-user"] {
        background: var(--gradient);
        color: white;
        box-shadow: var(--shadow);
    }

    /* Assistant message */
    .stChatMessage[data-testid="chat-message-assistant"] {
        background: var(--assistant);
        color: var(--text);
        box-shadow: var(--shadow);
    }

    /* Chat input */
    .stChatInput {
        position: sticky;
        bottom: 1.5rem;
        background: transparent;
    }

    textarea {
        border-radius: 16px !important;
        padding: 14px !important;
        border: 1px solid #e5e7eb !important;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 4. CLIENT SETUP
# -----------------------------------------------------------------------------
TEMPERATURE = 0.7
MAX_TOKENS = 2048
MODEL_ID = "HuggingFaceTB/SmolLM3-3B:hf-inference"

HF_TOKEN = os.getenv("HF_TOKEN")
if not HF_TOKEN:
    st.error("⚠️ HF_TOKEN is missing.")
    st.stop()

client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key=HF_TOKEN,
)

# -----------------------------------------------------------------------------
# 5. SESSION STATE
# -----------------------------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# -----------------------------------------------------------------------------
# 6. SIDEBAR
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown(
        f"""
        <div style="display:flex; justify-content:center; margin-bottom:12px;">
            <img src="data:image/png;base64,{LOGO_BASE64}"
                 style="width:72px; height:72px; image-rendering: crisp-edges;" />
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("### **Verona AI**")
    st.caption("Your intelligent assistant")

    st.divider()

    st.markdown(f"💬 **Messages:** {len(st.session_state.messages)}")

    if st.button("🆕 New Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.divider()
    st.caption("Powered by Hugging Face")

# -----------------------------------------------------------------------------
# 7. MAIN HEADER
# -----------------------------------------------------------------------------
st.markdown('<div class="title-text">Verona AI</div>', unsafe_allow_html=True)

if not st.session_state.messages:
    st.markdown(
        '<div class="subtitle-text">Hello. How can I help you today?</div>',
        unsafe_allow_html=True
    )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("📝 Draft an email", use_container_width=True):
            st.session_state.messages.append({
                "role": "user",
                "content": "Draft a professional email to a client about a project update."
            })
            st.rerun()

    with col2:
        if st.button("🧠 Brainstorm ideas", use_container_width=True):
            st.session_state.messages.append({
                "role": "user",
                "content": "Brainstorm 5 creative names for a new coffee shop."
            })
            st.rerun()

# -----------------------------------------------------------------------------
# 8. DISPLAY CHAT HISTORY
# -----------------------------------------------------------------------------
for msg in st.session_state.messages:
    avatar = "👤" if msg["role"] == "user" else LOGO_PATH
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

# -----------------------------------------------------------------------------
# 9. CHAT INPUT & STREAMING
# -----------------------------------------------------------------------------
if prompt := st.chat_input("Message Verona…"):
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar=LOGO_PATH):
        placeholder = st.empty()
        full_response = ""

        try:
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

                full_response += delta

                if "<think>" in full_response and "</think>" not in full_response:
                    placeholder.markdown(
                        "<span style='color:#6b7280; font-style:italic;'>Verona is thinking…</span>",
                        unsafe_allow_html=True
                    )
                else:
                    clean = full_response.split("</think>")[-1]
                    placeholder.markdown(clean + "▌")

            final = full_response.split("</think>")[-1].strip()
            placeholder.markdown(final)

            st.session_state.messages.append({
                "role": "assistant",
                "content": final
            })

        except Exception as e:
            st.error(f"Error: {e}")
