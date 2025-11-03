from flask import Flask, render_template, request, jsonify
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

app = Flask(__name__)

# Load small, free model that runs on Render's CPU
model_name = "microsoft/phi-2"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

# Store last few messages (short-term memory)
conversation_history = []

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat_api():
    global conversation_history
    user_input = request.json["message"]

    # Add the new user message to memory
    conversation_history.append(f"User: {user_input}")

    # Keep memory short (last 5 turns)
    if len(conversation_history) > 10:
        conversation_history = conversation_history[-10:]

    # Build Verona’s personality prompt
    prompt = (
        "You are Verona, a kind, friendly, and helpful AI assistant. "
        "You speak naturally, explain things clearly, and sometimes show a bit of warmth. "
        "Here’s the recent conversation:\n"
        + "\n".join(conversation_history)
        + "\nVerona:"
    )

    # Generate response
    inputs = tokenizer(prompt, return_tensors="pt")
    outputs = model.generate(**inputs, max_new_tokens=150)
    reply = tokenizer.decode(outputs[0], skip_special_tokens=True)

    # Extract only Verona's latest reply
    reply = reply.split("Verona:")[-1].strip()
    conversation_history.append(f"Verona: {reply}")

    return jsonify({"reply": reply})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
