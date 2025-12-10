{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": 2,
   "id": "140a05b1-b71b-4953-bf00-5d6f8cc8b38c",
   "metadata": {},
   "outputs": [
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "2025-12-10 21:09:30.021 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.\n",
      "2025-12-10 21:09:30.024 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.\n",
      "2025-12-10 21:09:30.025 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.\n",
      "2025-12-10 21:09:30.028 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.\n",
      "2025-12-10 21:09:30.028 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.\n",
      "2025-12-10 21:09:30.031 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.\n",
      "2025-12-10 21:09:30.037 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.\n",
      "2025-12-10 21:09:30.090 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.\n",
      "2025-12-10 21:09:30.092 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.\n",
      "2025-12-10 21:09:30.098 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.\n",
      "2025-12-10 21:09:30.101 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.\n",
      "2025-12-10 21:09:30.105 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.\n",
      "2025-12-10 21:09:30.108 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.\n",
      "2025-12-10 21:09:30.108 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.\n",
      "2025-12-10 21:09:30.108 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.\n"
     ]
    }
   ],
   "source": [
    "import os\n",
    "import streamlit as st\n",
    "from openai import OpenAI\n",
    "\n",
    "# -----------------------------\n",
    "# CONFIG\n",
    "# -----------------------------\n",
    "st.set_page_config(page_title=\"Verona AI\", page_icon=\"🤖\")\n",
    "st.title(\"🤖 Verona AI\")\n",
    "st.caption(\"A general-purpose AI assistant\")\n",
    "\n",
    "# ✅ Put token in environment variable (temporary fallback allowed)\n",
    "HF_TOKEN = os.getenv(\"HF_TOKEN\", \"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\")\n",
    "\n",
    "client = OpenAI(\n",
    "    base_url=\"https://router.huggingface.co/v1\",\n",
    "    api_key=HF_TOKEN,\n",
    ")\n",
    "\n",
    "MODEL_ID = \"HuggingFaceTB/SmolLM3-3B:hf-inference\"\n",
    "\n",
    "# -----------------------------\n",
    "# SESSION STATE\n",
    "# -----------------------------\n",
    "if \"messages\" not in st.session_state:\n",
    "    st.session_state.messages = []\n",
    "\n",
    "# Display chat history\n",
    "for msg in st.session_state.messages:\n",
    "    with st.chat_message(msg[\"role\"]):\n",
    "        st.markdown(msg[\"content\"])\n",
    "\n",
    "# -----------------------------\n",
    "# CHAT INPUT\n",
    "# -----------------------------\n",
    "if prompt := st.chat_input(\"Ask me anything...\"):\n",
    "    # Save user message\n",
    "    st.session_state.messages.append({\"role\": \"user\", \"content\": prompt})\n",
    "    with st.chat_message(\"user\"):\n",
    "        st.markdown(prompt)\n",
    "\n",
    "    # Call HF Router\n",
    "    with st.chat_message(\"assistant\"):\n",
    "        with st.spinner(\"Thinking...\"):\n",
    "            try:\n",
    "                completion = client.chat.completions.create(\n",
    "                    model=MODEL_ID,\n",
    "                    messages=st.session_state.messages,\n",
    "                )\n",
    "\n",
    "                reply = completion.choices[0].message.content\n",
    "\n",
    "                # Remove <think> block if present\n",
    "                if \"<think>\" in reply:\n",
    "                    reply = reply.split(\"</think>\")[-1].strip()\n",
    "\n",
    "            except Exception as e:\n",
    "                reply = f\"❌ Error: {e}\"\n",
    "\n",
    "        st.markdown(reply)\n",
    "\n",
    "    st.session_state.messages.append(\n",
    "        {\"role\": \"assistant\", \"content\": reply}\n",
    "    )\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "3984dbb8-d786-4101-9beb-ce8f0c1be71f",
   "metadata": {},
   "outputs": [],
   "source": []
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3 (ipykernel)",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.10.9"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}
