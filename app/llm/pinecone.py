
from typing import List
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone as PineconeLLM, ServerlessSpec

from llm.documents import calculate_chunk_ids
from llm.settings import llm_settings, GOOGLE_GEN_AI_EMBEDDING

class Pinecone:
    def __init__(self):
        self.collection_name = ""
        self.pinecone = PineconeLLM(api_key=llm_settings.PINECONE_API_KEY)
        self.vector_store = None

    def _open_collection(self, collection_name: str):
        self._create_index_if_not_exists(collection_name)
        self.collection_name = collection_name
        self.vector_store = PineconeVectorStore(
            index_name=self.collection_name,
            embedding=GOOGLE_GEN_AI_EMBEDDING(),
        )

    def _create_index_if_not_exists(self, collection_name: str):
        list_indexes = self.pinecone.list_indexes().names()
        if collection_name not in list_indexes:
            self.pinecone.create_index(
                collection_name, 
                dimension=768,
                spec=ServerlessSpec(
                    cloud="aws",
                    region="us-east-1"
                )
            )

    def add_documents(self, collection_name: str, chunks) -> bool:
        try:
            self._open_collection(collection_name)
            # Calculate Page IDs.
            chunks_with_ids = calculate_chunk_ids(chunks)

            new_chunks = []
            for chunk in chunks_with_ids:        
                new_chunks.append(chunk)

            if len(new_chunks):
                print(f"👉 Adding new documents: {len(new_chunks)}")
                new_chunk_ids = [chunk.metadata["id"] for chunk in new_chunks]
                self.vector_store.add_documents(new_chunks, ids=new_chunk_ids)
            else:
                print("✅ No new documents to add")
            return True
        except Exception as e:
            print(f"Error adding documents: {e}")
            return False

    def search(self, collection_name: str, query: str) -> List[str]:
        self._open_collection(collection_name)
        docs = self.vector_store.similarity_search_with_score(query)
        results = []
        for doc in docs:
            results.append(doc[0].page_content)
        return results
    
        