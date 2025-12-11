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
    layout="centered",
    initial_sidebar_state="auto"
)

# Custom CSS to mimic a cleaner, "Gemini-like" UI
st.markdown("""
<style>
    /* Hide the Streamlit main menu and footer for a cleaner look */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Tighten up the top padding */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 5rem;
    }

    /* Custom Title Style */
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
        margin-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. SETUP CLIENT & SIDEBAR
# -----------------------------------------------------------------------------

# Sidebar for controls
with st.sidebar:
    st.title("⚙️ Controls")
    
    # Model Configuration
    temperature = st.slider("Creativity (Temperature)", 0.0, 1.0, 0.7)
    max_tokens = st.slider("Max Length", 256, 4096, 2048)
    
    st.divider()
    
    # Clear Chat Button
    if st.button("🗑️ Clear Conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")
    st.caption("Powered by HuggingFace Inference & SmolLM3")

# Initialize Client
HF_TOKEN = os.getenv("HF_TOKEN")

if not HF_TOKEN:
    st.error("⚠️ **HF_TOKEN** is missing! Please check your `.env` or Streamlit secrets.")
    st.stop()

client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key=HF_TOKEN,
)

MODEL_ID = "HuggingFaceTB/SmolLM3-3B:hf-inference"

# -----------------------------------------------------------------------------
# 3. SESSION STATE & CHAT HISTORY
# -----------------------------------------------------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []

# Title Area
st.markdown('<div class="title-text">Verona AI</div>', unsafe_allow_html=True)

# If chat is empty, show a welcoming "Hero" section
if not st.session_state.messages:
    st.markdown('<div class="subtitle-text">Hello! I\'m Verona. How can I help you today?</div>', unsafe_allow_html=True)
    
    # Optional: Quick start suggestions
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📝 Write a poem about code", use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": "Write a short poem about coding."})
            st.rerun()
    with col2:
        if st.button("🐍 Explain Python lists", use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": "Explain Python lists in simple terms."})
            st.rerun()

# Display Chat History
for msg in st.session_state.messages:
    # Use different avatars for distinct visual separation
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
            # Create a streaming request
            stream = client.chat.completions.create(
                model=MODEL_ID,
                messages=st.session_state.messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True,  # ENABLE STREAMING
            )
            
            # Process the stream
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    full_response += content
                    
                    # Clean <think> tags dynamically for display
                    # (Simple logic: if we see the end tag, split. 
                    # Complex logic is hard in real-time streaming, so we display raw 
                    # during stream, and clean it up after)
                    display_text = full_response
                    if "</think>" in display_text:
                        display_text = display_text.split("</think>")[-1].strip()
                    elif "<think>" in display_text:
                        # If we are currently "thinking", show a loading indicator
                        display_text = "Let me think about that..."
                        
                    message_placeholder.markdown(display_text + "▌")
            
            # Final cleanup of <think> tags
            if "<think>" in full_response:
                final_clean_reply = full_response.split("</think>")[-1].strip()
            else:
                final_clean_reply = full_response

            message_placeholder.markdown(final_clean_reply)
            
            # 3. Save to History
            st.session_state.messages.append({"role": "assistant", "content": final_clean_reply})

        except Exception as e:
            st.error(f"An error occurred: {e}")
