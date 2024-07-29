import os
from langchain_openai import OpenAIEmbeddings

os.environ['OPENAI_API_KEY'] = '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'
os.environ['PINECONE_API_KEY'] = '759eb8d6-89f5-4054-8003-d55aebc5aa2e'

embeddings = OpenAIEmbeddings()

def get_embedding_function():        
    return embeddings
