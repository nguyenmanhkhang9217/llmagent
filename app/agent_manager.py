import os
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import PodSpec, pinecone
from langchain.prompts import ChatPromptTemplate
from langchain_core.documents import Document
# from langchain_openai import OpenAIEmbeddings
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
from documents import load_documents, split_documents, add_to_vectordb
from settings import googleGenAIApiKey, PROMPT_TEMPLATE, get_embedding_function


class AgentManager:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.7, top_p=0.85, api_key=googleGenAIApiKey)
        self.pinecone = pinecone.Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        self.index_name = "gemini-test"

    def create_index_if_not_exists(self, index_name: str):
        list_indexes = self.pinecone.list_indexes().names()
        if index_name not in list_indexes:
            self.pinecone.create_index(index_name, dimension=1536)  # Adjust dimension based on your embeddings

    

    def chat_with_agent(self, agent_id: int, message: str):
        # Ensure the index for the specific agent exists
        # index_name = f"agent-{agent_id}-conversations"
        # self.create_index_if_not_exists(self.index_name)

        conversation_history = message

        if "document" in message.lower() or "file" in message.lower():
            index = PineconeVectorStore(index_name=self.index_name, embedding=get_embedding_function())
            
            # this code below will quote the information from documents
            docs = index.similarity_search_with_score(query=message)
            context_text = "\n\n".join([doc.page_content for doc, _score in docs])
            prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
            prompt = prompt_template.format(context=context_text, question=message)
            
            # Append new user input to conversation history
            conversation_history = prompt

        # Generate a response using the LLM
        # response = self.llm(conversation_history)
        response_text = self.llm.invoke(conversation_history)

        # Save conversation to a file
        self.save_conversation(agent_id, message, response_text)


        return response_text

    def save_conversation(self, agent_id: int, message: str, response: str):
        conversation = f"Question: {message}\nAnswer: {response}\n\n"
        file_path = f"conversations/{agent_id}_conversation.txt"
        
        # Ensure the directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Append the new conversation to the file
        with open(file_path, "a") as file:
            file.write(conversation)
        
        # Add file to the vector database
        self.add_file_to_agent(file_path)

    def add_file_to_agent(self, file_path: str):

        document = load_documents(file_path)
        chunks = split_documents(document)
        add_to_vectordb(self.index_name, chunks)

        # Remove the file from the current folder
        if os.path.exists(file_path):
            os.remove(file_path)
