# backend/app/services/llm.py

import google.generativeai as gemini

gemini.configure(api_key="YOUR_API_KEY")

def generate_response(prompt: str) -> str:
    response = gemini.generate(prompt)
    return response['text']