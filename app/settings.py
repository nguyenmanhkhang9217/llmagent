import os
from langchain_google_genai import GoogleGenerativeAIEmbeddings

googleGenAIApiKey = os.getenv("GOOGLE_API_KEY")
PROMPT_TEMPLATE = """
Answer the question based only on the following context:

{context}

---

Answer the question based on the above context: {question}
"""

def get_embedding_function():        
        return GoogleGenerativeAIEmbeddings(model="models/embedding-001", api_key=googleGenAIApiKey)