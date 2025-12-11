# Add this at the top with your other imports
from huggingface_hub import InferenceClient

# ---------------------------
# TOKEN SETUP (unchanged)
# ---------------------------
HF_TOKEN = os.getenv("HF_TOKEN")

if not HF_TOKEN:
    st.error("HF_TOKEN not set. Please configure it in Streamlit Secrets.")
    st.stop()

# Supported free model (same)
MODEL_ID = "HuggingFaceTB/SmolLM2-1.7B-Instruct"

# Create the HF Inference client
client = InferenceClient(token=HF_TOKEN)

# ---------------------------
# In the place where you previously used client.chat.completions.create(...)
# Replace that try/except block with this
# ---------------------------

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

    # Hugging Face InferenceClient supports chat completion directly:
    # it expects a list of messages (role/content dicts).
    # Use chat_completion, passing model and messages
    hf_resp = client.chat_completion(
        model=MODEL_ID,
        messages=conversation,
        # optional: max_new_tokens=256, temperature=0.7, stream=False
    )

    # The HF response shape can vary by version/provider. Try common fields:
    reply = None

    # if it follows choice/message style (OpenAI-like)
    try:
        if isinstance(hf_resp, dict) and "choices" in hf_resp:
            reply = hf_resp["choices"][0]["message"]["content"]
    except Exception:
        pass

    # fallback: some HF clients return 'generated_text' or 'content'
    if not reply:
        # Inspect returned object safely (convert to string)
        # Many versions return a simple object with text under `.choices` or `generated_text`
        if isinstance(hf_resp, dict) and "generated_text" in hf_resp:
            reply = hf_resp["generated_text"]
        elif isinstance(hf_resp, dict) and "message" in hf_resp and "content" in hf_resp["message"]:
            reply = hf_resp["message"]["content"]
        else:
            # last fallback: stringify the response (useful for debugging)
            reply = str(hf_resp)

    # clean up any <think> tags like you already had
    reply = clean_response(reply)

except Exception as e:
    reply = f"❌ Error: {str(e)}"
