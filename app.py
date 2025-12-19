import os
import streamlit as st
from openai import OpenAI
import time

# -----------------------------------------------------------------------------
# 1. PAGE CONFIGURATION
# -----------------------------------------------------------------------------
LOGO_PATH = "assets/Verona AI Logo.png" 
FAVICON_PATH = "assets/Verona AI Logo.png"

st.set_page_config(
    page_title="Verona AI",
    page_icon=FAVICON_PATH,
    layout="centered",
)

# -----------------------------------------------------------------------------
# 2. GLOBAL STYLING (Premium Minimal UI)
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    #MainMenu, footer, header {visibility: hidden;}

    .block-container {
        padding-top: 2.5rem;
        padding-bottom: 6rem;
        max-width: 720px;
    }

    /* Title */
    .title-text {
        font-family: 'Inter', sans-serif;
        background: linear-gradient(90deg, #5B8CFF, #9B5CFF);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        font-size: 3rem;
        text-align: center;
        margin-bottom: 0.3rem;
    }

    .subtitle-text {
        text-align: center;
        color: #777;
        font-size: 1.05rem;
        margin-bottom: 2.5rem;
    }

    /* Chat input */
    .stChatInput {
        position: sticky;
        bottom: 1rem;
        background: transparent;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #fafafa;
        border-right: 1px solid #eee;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 3. CLIENT SETUP
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
# 4. SESSION STATE
# -----------------------------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# -----------------------------------------------------------------------------
# 5. SIDEBAR (CHAT HISTORY + BRANDING)
# -----------------------------------------------------------------------------
with st.sidebar:
    st.image(LOGO_PATH, width=80)
    st.markdown("### **Verona AI**")
    st.caption("Your intelligent assistant")

    st.divider()

    st.markdown(f"💬 **Messages:** {len(st.session_state.messages)}")

    if st.button("🆕 New Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.divider()
    st.caption("Powered by Hugging Face Inference")

# -----------------------------------------------------------------------------
# 6. MAIN HEADER
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
# 7. DISPLAY CHAT HISTORY
# -----------------------------------------------------------------------------
for msg in st.session_state.messages:
    avatar = "👤" if msg["role"] == "user" else LOGO_PATH
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

# -----------------------------------------------------------------------------
# 8. CHAT INPUT & STREAMING RESPONSE
# -----------------------------------------------------------------------------
if prompt := st.chat_input("Message Verona..."):
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

                # Hide thinking blocks
                if "<think>" in full_response and "</think>" not in full_response:
                    placeholder.markdown("💭 *Verona is thinking…*")
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
