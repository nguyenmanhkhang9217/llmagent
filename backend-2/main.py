from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx
import json
from dotenv import load_dotenv
import textwrap

import google.generativeai as genai
import os

from IPython.display import display
from IPython.display import Markdown

load_dotenv()
genai.configure(api_key=os.getenv("API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')

app = FastAPI()

class ChatRequest(BaseModel):
    prompt: str

class ChatResponse(BaseModel):
    response: str

# Initialize the GenAI client and start a chat session
chat_session = model.start_chat(history=[])

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    prompt = request.prompt
    try:
        # Send message to the chat session
        response = chat_session.send_message(prompt)
        generated_response = response.text
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return ChatResponse(response=generated_response)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9000)
#--------
#GPT-3.5-turbo

# app = FastAPI()

# class ChatRequest(BaseModel):
#     prompt: str

# class ChatResponse(BaseModel):
#     response: str

# @app.post("/api/chat", response_model=ChatResponse)
# async def chat(request: ChatRequest):
#     prompt = request.prompt
#     print(f"Received prompt: {prompt}")
#     try:
#         async with httpx.AsyncClient() as client:
#             response = await client.post(
#                 "https://api.openai.com/v1/chat/completions",
#                 headers={
#                     "Content-Type": "application/json",
#                     "Authorization": f"Bearer sk-proj-5FE9Nz6fHJnFS6i7UFjPT3BlbkFJeCdLiXqPJhIezVFFdPB8"
#                     },
#                 json={
#                     "model": "gpt-3.5-turbo",
#                     "messages": [{"role": "user", "content": prompt}],
#                     "temperature": 0.7,
#                 }
#             )
#             response_data = response.json()
#             print(response_data)
#             generated_response = response_data["choices"][0]["message"]["content"].strip()
#     except Exception as e:
#         print(f"Error processing request: {e}")
#         raise HTTPException(status_code=500, detail=f"Error processing request: {e}")
#     return ChatResponse(response=generated_response)

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=9000)