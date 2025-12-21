import os
from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from openai import OpenAI

import firebase_admin
from firebase_admin import credentials, auth

# -----------------------------------------------------------------------------
# Firebase Admin Init
# -----------------------------------------------------------------------------
cred = credentials.Certificate("firebase-service.json")
firebase_admin.initialize_app(cred)

def verify_user(request: Request):
    header = request.headers.get("Authorization")
    if not header or not header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Unauthorized")

    token = header.replace("Bearer ", "")
    try:
        decoded = auth.verify_id_token(token)
        return decoded["uid"]
    except:
        raise HTTPException(status_code=401, detail="Invalid token")

# -----------------------------------------------------------------------------
# FastAPI App
# -----------------------------------------------------------------------------
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten later
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------------------------------------------------------
# AI Client
# -----------------------------------------------------------------------------
client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key=os.getenv("HF_TOKEN"),
)

# -----------------------------------------------------------------------------
# Chat Endpoint (Protected)
# -----------------------------------------------------------------------------
@app.post("/chat")
async def chat(request: Request, user_id: str = Depends(verify_user)):
    data = await request.json()
    messages = data["messages"]

    stream = client.chat.completions.create(
        model="HuggingFaceTB/SmolLM3-3B:hf-inference",
        messages=messages,
        stream=True,
    )

    def event_stream():
        for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta

    return StreamingResponse(event_stream(), media_type="text/plain")
