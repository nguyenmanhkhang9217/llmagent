import os

from langchain_google_genai import GoogleGenerativeAIEmbeddings
from pydantic_settings import BaseSettings

class LLMSettings(BaseSettings):
        CHROMA_HOST: str = os.environ['CHROMA_HOST']
        CHROMA_PORT: int = os.environ['CHROMA_PORT']
        PINECONE_API_KEY: str = os.environ['PINECONE_API_KEY']
        GOOGLE_API_KEY: str = os.environ['GOOGLE_API_KEY']      
        PROMPT_TEMPLATE: str = """
You are an expert consultant helping executive advisors to get relevant information from internal documents.

Generate your response by following the steps below:
1. Recursively break down the question into smaller questions.
2. For each question/directive:
        2a. Select the most relevant information from the context in light of the conversation history.
3. Generate a draft response using selected information.
4. Remove duplicate content from draft response.
5. Generate your final response after adjusting it to increase accuracy and relevance.
6. Do not try to summarise the answers, explain it properly.
6. Only show your final response! 

Constraints:
1. DO NOT PROVIDE ANY EXPLANATION OR DETAILS OR MENTION THAT YOU WERE GIVEN CONTEXT.
2. Don't mention that you are not able to find the answer in the provided context.
3. Don't make up the answers by yourself.
4. Try your best to provide answer from the given context.

CONTENT:
{context}

==============================================================
Based on the above context, please provide the answer to the following question:
{question}
"""

llm_settings = LLMSettings()

def GOOGLE_GEN_AI_EMBEDDING():
        return GoogleGenerativeAIEmbeddings(
                model="models/embedding-001", 
                api_key=llm_settings.GOOGLE_API_KEY
        )