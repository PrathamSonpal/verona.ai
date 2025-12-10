import os
import streamlit as st
from openai import OpenAI

# -----------------------------
# CONFIG
# -----------------------------
st.set_page_config(page_title="Verona AI", page_icon="🤖")
st.title("🤖 Verona AI")
st.caption("A general-purpose AI assistant")

client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key=HF_TOKEN,
)

MODEL_ID = "HuggingFaceTB/SmolLM3-3B:hf-inference"

# -----------------------------
# SESSION STATE
# -----------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# -----------------------------
# CHAT INPUT
# -----------------------------
if prompt := st.chat_input("Ask me anything..."):
    # Save user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Call HF Router
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                completion = client.chat.completions.create(
                    model=MODEL_ID,
                    messages=st.session_state.messages,
                )

                reply = completion.choices[0].message.content

                # Remove <think> block if present
                if "<think>" in reply:
                    reply = reply.split("</think>")[-1].strip()

            except Exception as e:
                reply = f"❌ Error: {e}"

        st.markdown(reply)

    st.session_state.messages.append(
        {"role": "assistant", "content": reply}
    )
