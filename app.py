import os
import streamlit as st
from openai import OpenAI
import time

# -----------------------------------------------------------------------------
# 1. PAGE CONFIGURATION & STYLING
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Verona AI",
    page_icon="✨",
    layout="centered"
)

# Custom CSS for a minimalistic, "Gemini-like" UI
st.markdown("""
<style>
    /* Hide the Streamlit main menu, footer, and header */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Adjust padding to center content nicely */
    .block-container {
        padding-top: 3rem;
        padding-bottom: 5rem;
    }

    /* Gradient Title */
    .title-text {
        font-family: 'Inter', sans-serif;
        background: -webkit-linear-gradient(45deg, #4A90E2, #9013FE);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700;
        font-size: 3rem;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    
    .subtitle-text {
        text-align: center;
        color: #666;
        font-size: 1.1rem;
        margin-bottom: 3rem;
    }
    
    /* Input field styling adjustments (Streamlit default is okay, but we clean around it) */
    .stChatInput {
        padding-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. SETUP CLIENT
# -----------------------------------------------------------------------------

# Internal Settings (Hidden from user)
TEMPERATURE = 0.7
MAX_TOKENS = 2048
MODEL_ID = "HuggingFaceTB/SmolLM3-3B:hf-inference"

HF_TOKEN = os.getenv("HF_TOKEN")

if not HF_TOKEN:
    st.error("⚠️ **HF_TOKEN** is missing! Please check your `.env` or Streamlit secrets.")
    st.stop()

client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key=HF_TOKEN,
)

# -----------------------------------------------------------------------------
# 3. SESSION STATE & CHAT HISTORY
# -----------------------------------------------------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []

# Title Area
st.markdown('<div class="title-text">Verona AI</div>', unsafe_allow_html=True)

# Hero Section: Only shows when chat is empty
if not st.session_state.messages:
    st.markdown('<div class="subtitle-text">Hello. How can I help you today?</div>', unsafe_allow_html=True)
    
    # Simple starter suggestions
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📝 Draft an email", use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": "Draft a professional email to a client about a project update."})
            st.rerun()
    with col2:
        if st.button("🧠 Brainstorm ideas", use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": "Brainstorm 5 creative names for a new coffee shop."})
            st.rerun()

# Display Chat History
for msg in st.session_state.messages:
    avatar = "👤" if msg["role"] == "user" else "✨"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

# -----------------------------------------------------------------------------
# 4. CHAT LOGIC WITH STREAMING
# -----------------------------------------------------------------------------

if prompt := st.chat_input("Message Verona..."):
    # 1. Add User Message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    # 2. Generate Assistant Response
    with st.chat_message("assistant", avatar="✨"):
        message_placeholder = st.empty()
        full_response = ""
        
        try:
            stream = client.chat.completions.create(
                model=MODEL_ID,
                messages=st.session_state.messages,
                temperature=TEMPERATURE,
                max_tokens=MAX_TOKENS,
                stream=True,
            )
            
            # Process the stream
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    full_response += content
                    
                    # Logic to hide <think> blocks while streaming
                    display_text = full_response
                    if "</think>" in display_text:
                        # Only show what comes AFTER the thinking block
                        display_text = display_text.split("</think>")[-1].strip()
                    elif "<think>" in display_text:
                        # While thinking, show a subtle loading state
                        display_text = "Thinking..."
                        
                    message_placeholder.markdown(display_text + "▌")
            
            # Final cleanup
            if "<think>" in full_response:
                final_clean_reply = full_response.split("</think>")[-1].strip()
            else:
                final_clean_reply = full_response

            message_placeholder.markdown(final_clean_reply)
            
            # 3. Save to History
            st.session_state.messages.append({"role": "assistant", "content": final_clean_reply})

        except Exception as e:
            st.error(f"An error occurred: {e}")
