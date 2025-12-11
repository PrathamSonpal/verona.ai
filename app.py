# Add near top with other imports
import requests

# TOKEN SETUP (unchanged)
HF_TOKEN = os.getenv("HF_TOKEN")
if not HF_TOKEN:
    st.error("HF_TOKEN not set. Please configure it in Streamlit Secrets.")
    st.stop()

MODEL_ID = "HuggingFaceTB/SmolLM2-1.7B-Instruct"  # same model id

HF_ROUTER = f"https://router.huggingface.co/hf-inference/models/{MODEL_ID}/v1/chat/completions"
HEADERS = {"Authorization": f"Bearer {HF_TOKEN}", "Content-Type": "application/json"}

# Replace the portion in your try/except where you call the client with this:
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
        # optional tuning params:
        # "max_new_tokens": 256,
        # "temperature": 0.7,
        # "top_p": 0.95,
        # "stream": False
    }

    resp = requests.post(HF_ROUTER, headers=HEADERS, json=payload, timeout=60)
    if resp.status_code != 200:
        raise Exception(f"HF API error {resp.status_code}: {resp.text}")

    data = resp.json()

    # Parse common response shapes:
    reply = None

    if isinstance(data, dict):
        # OpenAI-like chat completion format
        if "choices" in data and isinstance(data["choices"], list) and data["choices"]:
            # many HF router responses mimic OpenAI shape:
            choice = data["choices"][0]
            # try different places where content may be
            if isinstance(choice, dict):
                if "message" in choice and isinstance(choice["message"], dict):
                    reply = choice["message"].get("content")
                elif "text" in choice:
                    reply = choice.get("text")
                elif "delta" in choice and isinstance(choice["delta"], dict):
                    # if streaming-like single chunk
                    reply = choice["delta"].get("content") or choice["delta"].get("text")
        # fallbacks
        if not reply and "generated_text" in data:
            reply = data["generated_text"]
        if not reply and "message" in data and isinstance(data["message"], dict):
            reply = data["message"].get("content")
    if not reply:
        # last resort: stringify
        reply = str(data)

    reply = clean_response(reply)

except Exception as e:
    reply = f"❌ Error: {str(e)}"
