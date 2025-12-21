from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from openai import OpenAI
import os

app = FastAPI()

client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key=os.getenv("HF_TOKEN")
)

@app.post("/chat")
async def chat(payload: dict):
    messages = payload["messages"]

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
