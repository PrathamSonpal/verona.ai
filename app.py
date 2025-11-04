from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

# Public, free model that never needs manual approval
API_URL = "https://router.huggingface.co/hf-inference/models/google/gemma-2b"

HEADERS = {"Authorization": "Bearer hf_UNfhbOLoAVeawjWWlnTdkfwDPAyCAuxFAvhf_VkUsYtbufZHKLmxPvCPdOXwvbHipnUoWwM"}

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat_api():
    user_input = request.json["message"]
    payload = {"inputs": f"User: {user_input}\nVerona:"}

    try:
        response = requests.post(API_URL, headers=HEADERS, json=payload, timeout=30)
        data = response.json()
        print("DEBUG HF RESPONSE:", data)  # visible in Render logs

        # Extract model reply if it exists
        if isinstance(data, list) and "generated_text" in data[0]:
            reply = data[0]["generated_text"]
        elif "error" in data:
            reply = f"Model error: {data['error']}"
        else:
            reply = "Hmm, I had trouble thinking. Please try again."
    except Exception as e:
        reply = f"Error: {str(e)}"

    return jsonify({"reply": reply})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

