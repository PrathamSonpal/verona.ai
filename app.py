import os
import json
import requests
import streamlit as st

# ---------------------------------
# PAGE CONFIG
# ---------------------------------
st.set_page_config(page_title="Verona AI", page_icon="🤖")
st.title("🤖 Verona AI — Free & Smart")
st.caption("Using Hugging Face SmolLM2 1.7B Instruct (via HF router)")

# ---------------------------------
# TOKEN SETUP
# ---------------------------------
HF_TOKEN = os.getenv("HF_TOKEN")
if not HF_TOKEN:
    st.error("HF_TOKEN not set. Please configure it in Streamlit Secrets (Manage app → Secrets).")
    st.stop()

# Supported free model (change if needed)
MODEL_ID = "HuggingFaceTB/SmolLM2-1.7B-Instruct"
HF_ROUTER = f"https://router.huggingface.co/hf-inference/models/{MODEL_ID}/v1/chat/completions"
HEADERS = {"Authorization": f"Bearer {HF_TOKEN}", "Content-Type": "application/json"}

# ---------------------------------
# CLEAN RESPONSE
# ---------------------------------
def clean_response(text):
    if text is None:
        return ""
    if "<think>" in text:
        text = text.split("</think>")[-1].strip()
    text = text.replace("<think>", "").replace("</think>", "")
    return text

# ---------------------------------
# SAVE/LOAD CHAT HISTORY
# ---------------------------------
def save_history():
    try:
        with open("history.json", "w") as f:
            json.dump(st.session_state.messages, f)
    except Exception:
        # ignore write errors in cloud environment
        pass

def load_history():
    try:
        with open("history.json", "r") as f:
            st.session_state.messages = json.load(f)
    except Exception:
        st.session_state.messages = []

# ---------------------------------
# INITIALIZE SESSION
# ---------------------------------
if "messages" not in st.session_state:
    load_history()

# ---------------------------------
# DISPLAY CHAT HISTORY
# ---------------------------------
for msg in st.session_state.messages:
    avatar = "🤖" if msg.get("role") == "assistant" else "🙂"
    with st.chat_message(msg.get("role"), avatar=avatar):
        st.markdown(msg.get("content", ""))

# ---------------------------------
# USER INPUT
# ---------------------------------
if prompt := st.chat_input("Ask Verona anything..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    save_history()

    with st.chat_message("user", avatar="🙂"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("Verona is thinking..."):
            try:
                system_instruction = {
                    "role": "system",
                    "content": (
                        "You are Verona, a smart AI assistant. "
                        "Provide accurate and helpful answers. "
                        "Think before answering, but never reveal internal reasoning."
                    )
                }
                conversation = [system_instruction] + st.session_state.messages[-8:]

                payload = {
                    "model": MODEL_ID,
                    "messages": conversation,
                    # optionally tune these:
                    # "max_new_tokens": 256,
                    # "temperature": 0.7,
                }

                resp = requests.post(HF_ROUTER, headers=HEADERS, json=payload, timeout=60)
                if resp.status_code != 200:
                    # Surface the HF error to the user (helpful for debugging)
                    raise Exception(f"HF API error {resp.status_code}: {resp.text}")

                data = resp.json()

                # Try to parse common response shapes
                reply = None

                # OpenAI-like format
                if isinstance(data, dict) and "choices" in data and isinstance(data["choices"], list):
                    choice = data["choices"][0]
                    if isinstance(choice, dict):
                        if "message" in choice and isinstance(choice["message"], dict):
                            reply = choice["message"].get("content")
                        elif "text" in choice:
                            reply = choice.get("text")
                        elif "delta" in choice and isinstance(choice["delta"], dict):
                            reply = choice["delta"].get("content") or choice["delta"].get("text")

                # fallback shapes
                if not reply and isinstance(data, dict) and "generated_text" in data:
                    reply = data["generated_text"]
                if not reply and isinstance(data, dict) and "message" in data and isinstance(data["message"], dict):
                    reply = data["message"].get("content")

                if not reply:
                    # last resort: stringify the response (useful for debugging)
                    reply = json.dumps(data, ensure_ascii=False)

                reply = clean_response(reply)

            except Exception as e:
                # Show error inline so you can see it in the app
                err_text = f"❌ Error: {str(e)}"
                st.error(err_text)
                reply = err_text

        st.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})
    save_history()
