# # backend/app/services/rag.py

# from elasticsearch import Elasticsearch
# from .llm import generate_response

# es = Elasticsearch(["http://localhost:9200"])

# def retrieve_documents(query: str):
#     response = es.search(
#         index="documents",
#         body={
#             "query": {
#                 "match": {
#                     "content": query
#                 }
#             }
#         }
#     )
#     return [doc["_source"] for doc in response["hits"]["hits"]]

# def generate_rag_response(prompt: str) -> str:
#     documents = retrieve_documents(prompt)
#     enhanced_prompt = f"{prompt} {' '.join(doc['content'] for doc in documents)}"
#     return generate_response(enhanced_prompt)

# app/routers/rag.py
from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from pydantic import BaseModel
from langchain_pinecone import PineconeVectorStore

from langchain.prompts import ChatPromptTemplate
# from langchain.document_loaders.pdf import PyPDFLoader
# from langchain.document_loaders.pdf import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from typing import List
from langchain.schema.document import Document
import google.generativeai as genai
import schemas, models
from sqlalchemy.orm import Session
from dependencies import get_db
# from langchain_google_genai import GoogleGenerativeAIEmbeddings
import os
from pathlib import Path
from pprint import pprint

from langchain.vectorstores import Pinecone
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from sentence_transformers import SentenceTransformer
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains.question_answering import load_qa_chain
from langchain import PromptTemplate
import pinecone
# os.environ['GOOGLE_GENAI_API_KEY'] = 'your-google-genai-api-key'
# Set up Pinecone environment
pinecone.init(api_key="YOUR_PINECONE_API_KEY", environment="YOUR_ENVIRONMENT")

# Initialize Pinecone index
index_name = "chatbot-memory"
pinecone.create_index(index_name, dimension=768)  # Adjust dimension based on your embeddings
index = pinecone.Index(index_name)

router = APIRouter()

PROMPT_TEMPLATE = """
Answer the question based only on the following context:

{context}

---

Answer the question based on the above context: {question}
"""

class QueryRequest(BaseModel):
    query_text: str

def get_embedding_function():
    # Define your embedding function here
    return GoogleGenerativeAIEmbeddings(model="models/embedding-001")

def query_rag(query_text: str):
    # Prepare the DB
    db = PineconeVectorStore(index_name='gemini-test', embedding=get_embedding_function())

    # Search the DB
    results = db.similarity_search_with_score(query_text, k=5)

    context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context_text, question=query_text)

    # Initialize Gemini-1.5 model
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.7, top_p=0.85)
    response_text = llm.invoke(prompt)

    sources = [doc.metadata.get("id", None) for doc, _score in results]
    formatted_response = f"Response: {response_text}\nSources: {sources}"
    print(formatted_response)
    return response_text
def store_chat_history(agent_id, user_message, agent_response):
    # Create embeddings for user message and agent response
    embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    user_embedding = embedding_model.embed(user_message)
    agent_embedding = embedding_model.embed(agent_response)
    
    # Create unique IDs for each message
    user_message_id = f"{agent_id}_user_{len(user_message)}"
    agent_response_id = f"{agent_id}_agent_{len(agent_response)}"
    
    # Upsert embeddings into Pinecone index
    index.upsert([
        (user_message_id, user_embedding, {"agent_id": agent_id, "message": user_message}),
        (agent_response_id, agent_embedding, {"agent_id": agent_id, "response": agent_response})
    ])

# Example usage
# store_chat_history("agent_1", "Hello, how are you?", "I'm fine, thank you!")

def retrieve_chat_memory(agent_id, query):
    # Create query embedding
    embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    query_embedding = embedding_model.embed(query)
    
    # Search for relevant chat history in Pinecone
    results = index.query(queries=[query_embedding], top_k=5, filter={"agent_id": agent_id})
    
    # Extract and return the most relevant past interactions
    memory = []
    for match in results["matches"]:
        memory.append(match["metadata"]["message"] if "message" in match["metadata"] else match["metadata"]["response"])
    
    return memory

# Example usage
chat_memory = retrieve_chat_memory("agent_1", "Tell me about our last conversation.")
print(chat_memory)

def generate_response(agent_id, user_message):
    chat_memory = retrieve_chat_memory(agent_id, user_message)
    
    # Combine chat memory and user message for context-aware response generation
    combined_input = "\n".join(chat_memory + [user_message])
    
    # Generate response using Langchain and Google Generative AI
    prompt_template = PromptTemplate(
        template="Based on the previous conversations and the current input, generate a response:\n\n{combined_input}",
        input_variables=["combined_input"]
    )
    
    qa_chain = load_qa_chain(llm=ChatGoogleGenerativeAI(), prompt=prompt_template)
    response = qa_chain.run(combined_input=combined_input)
    
    # Store the interaction
    store_chat_history(agent_id, user_message, response)
    
    return response

# Example usage
response = generate_response("agent_1", "Can you remind me what we discussed last time?")
print(response)


@app.post("/api/chat", response_model=schemas.ChatResponse)
async def chat(request: schemas.ChatRequest):
    agent_id = request.agent_id
    prompt = request.prompt
    try:
        # Generate response using the agent's memory
        generated_response = generate_response(agent_id, prompt)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return ChatResponse(response=generated_response)


@router.get("/chat/history/{agent_id}", response_model=schemas.ChatHistoryResponse)
async def get_chat_history(agent_id: int, db: Session = Depends(get_db)):
    chat_session = db.query(models.ChatSession).filter(models.ChatSession.agent_id == agent_id).first()
    if not chat_session:
        raise HTTPException(status_code=404, detail="Chat session not found for the agent")

    history_records = db.query(models.ChatHistory).filter(models.ChatHistory.chat_session_id == chat_session.id).all()
    messages = [record.message for record in history_records]
    responses = [record.response for record in history_records]

    return schemas.ChatHistoryResponse(messages=messages, responses=responses)

# @router.post("/query")
# async def query_rag(query_request: QueryRequest):
#     query_text = query_request.query_text
#     db = PineconeVectorStore(index_name='test1', embedding=get_embedding_function())
#     results = db.similarity_search_with_score(query_text, k=5)
#     context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
#     prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
#     prompt = prompt_template.format(context=context_text, question=query_text)
#     # model = Gemini(api_key=os.getenv('GEMINI_API_KEY'))
#     model = genai.GenerativeModel('gemini-1.5-flash')
#     response_text = model.send_message(prompt)
#     sources = [doc.metadata.get("id", None) for doc, _score in results]
#     formatted_response = {
#         "response": response_text,
#         "sources": sources
#     }
#     return formatted_response

@router.post("/upload")
async def upload_files(files: List[UploadFile] = File(...)):
    documents = []
    for file in files:
        if file.content_type != "application/pdf":
            raise HTTPException(status_code=400, detail="Only PDF files are supported.")
        content = await file.read()
        pdf_loader = PyPDFLoader(content)
        documents.extend(pdf_loader.load())

    chunks = split_documents(documents)
    add_to_db(chunks)
    return {"message": f"Successfully uploaded {len(files)} files and added to the vector store."}

def split_documents(documents: List[Document]):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=80,
        length_function=len,
        is_separator_regex=False,
    )
    return text_splitter.split_documents(documents)

def add_to_db(chunks: List[Document]):
    db = PineconeVectorStore(index_name='test1', embedding=get_embedding_function())
    chunks_with_ids = calculate_chunk_ids(chunks)
    new_chunks = [chunk for chunk in chunks_with_ids]
    if new_chunks:
        new_chunk_ids = [chunk.metadata["id"] for chunk in new_chunks]
        db.add_documents(new_chunks, ids=new_chunk_ids)

def calculate_chunk_ids(chunks):
    last_page_id = None
    current_chunk_index = 0
    for chunk in chunks:
        source = chunk.metadata.get("source")
        page = chunk.metadata.get("page")
        current_page_id = f"{source}:{page}"
        if current_page_id == last_page_id:
            current_chunk_index += 1
        else:
            current_chunk_index = 0
        chunk_id = f"{current_page_id}:{current_chunk_index}"
        last_page_id = current_page_id
        chunk.metadata["id"] = chunk_id
    return chunks


# @router.post("/chat", response_model=schemas.ChatResponse)
# async def chat(request: schemas.ChatRequest, db: Session = Depends(get_db)):
#     prompt = request.prompt
#     agent_id = request.agent_id

#     agent = db.query(schemas.Agent).filter(schemas.Agent.id == agent_id).first()
#     if not agent:
#         raise HTTPException(status_code=404, detail="Agent not found")

#     # Find or create a chat session for the agent
#     chat_session = db.query(models.ChatSession).filter(models.ChatSession.agent_id == agent_id).first()
#     if not chat_session:
#         genai.configure(api_key=os.getenv("API_KEY"))
#         model = genai.GenerativeModel('gemini-1.5-flash')
#         chat_session_obj = model.start_chat(history=[])
#         chat_session = models.ChatSession(agent_id=agent_id)
#         db.add(chat_session)
#         db.commit()
#         db.refresh(chat_session)
#     else:
#         # If a chat session exists, resume the session with history
#         history_records = db.query(models.ChatHistory).filter(models.ChatHistory.chat_session_id == chat_session.id).all()
#         history = [{"role": "user", "content": record.message} for record in history_records]
#         genai.configure(api_key=os.getenv("API_KEY"))
#         model = genai.GenerativeModel('gemini-1.5-flash')
#         chat_session_obj = model.start_chat(history=history)

#     try:
#         response = chat_session_obj.send_message(prompt)
#         generated_response = response.text
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

#     # Store the chat history in the database
#     chat_history = models.ChatHistory(chat_session_id=chat_session.id, message=prompt, response=generated_response)
#     db.add(chat_history)
#     db.commit()

#     return schemas.ChatResponse(response=generated_response)
