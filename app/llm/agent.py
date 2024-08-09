import time
import os
from enum import Enum
from typing import List
from threading import Thread

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate


from llm.documents import load_documents, split_documents
from llm.chroma import Chroma
from llm.pinecone import Pinecone
from llm.settings import llm_settings


class LLMType(Enum):
    CHROMA = 'chroma'
    PINECONE = 'pinecone'


class LLMAgent:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.7, top_p=0.85, api_key=llm_settings.GOOGLE_API_KEY)
        self.vectors = {}
        self.init_vectors()

    def init_vectors(self):
        self.vectors[LLMType.CHROMA] = Chroma()
        self.vectors[LLMType.PINECONE] = Pinecone()

    def add_file(self, 
                 llm_types: List[LLMType], 
                 collection_name: str, file_path: str
        )->bool:
        try:
            document = load_documents(file_path)
            chunks = split_documents(document)
            for llm_type in llm_types:
                if llm_type in self.vectors:
                    self.vectors[llm_type].add_documents(collection_name, chunks)
            
            if os.path.exists(file_path):
                os.remove(file_path)
            return True
        except Exception as e:
            print(f"Error adding file: {e}")
            return False

    def chat(self, 
             llm_types: List[LLMType], 
             collection_name: str, 
             message: str
        )-> str:
        try:
            contexts = []
            vector_threads = []
            time_start = time.time()
            for llm_type in llm_types:
                if llm_type in self.vectors:
                    print(f"Searching {llm_type} for {message}")
                    vector_threads.append(Thread(target=self._search_thread, args=(contexts, self.vectors[llm_type], collection_name, message)))
                    vector_threads[-1].start()
        
            for thread in vector_threads:
                thread.join()
            
            # Caculate time to search
            time_end = time.time()
            print(f"Time to search: {time_end - time_start}")

            context_string = "\n\n".join(contexts)

            template = ChatPromptTemplate.from_template(llm_settings.PROMPT_TEMPLATE)
            prompt = template.format(context=context_string, question=message)

            response = self.llm.invoke(prompt)

            result = response.content

            save_conversation_thread = Thread(target=self.save_conversation, args=(llm_types, collection_name, message, result))
            save_conversation_thread.start()

            return {
                "content": result,
            }
        except Exception as e:
            print(f"Error chatting with agent: {e}")
            return "I am sorry, I could not process your request at the moment."

    def _search_thread(self, contexts, vector, collection_name, query):
        for context in vector.search(collection_name, query):
            contexts.append(context)

    def save_conversation(
            self, 
            llm_types: List[LLMType], 
            collection_name: str, 
            message: str, 
            response: str
        )->bool:
        try:
            conversation = f"Question: {message}\nAnswer: {response}\n\n"
            file_path = f"conversations/{collection_name}_conversation.txt"
            with open(file_path, "a") as f:
                f.write(conversation)
            
            self.add_file(llm_types, collection_name, file_path)
            return True
        except Exception as e:
            print(f"Error saving conversation: {e}")
            return False
