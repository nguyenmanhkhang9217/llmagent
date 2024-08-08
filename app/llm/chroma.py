import os
from typing import List

from langchain_chroma import Chroma as ChromaVectorStore
from chromadb.config import Settings as ChromaSettings
import chromadb

from llm.documents import calculate_chunk_ids
from llm.settings import llm_settings, GOOGLE_GEN_AI_EMBEDDING



class Chroma:
    def __init__(self):
        self.collection_name = ""
        self.client = chromadb.HttpClient(
            host=llm_settings.CHROMA_HOST,
            port=llm_settings.CHROMA_PORT,
            settings=ChromaSettings(allow_reset=True),
        )
        self.vector_store = None

    def _open_collection(self, collection_name):
        self.collection_name = collection_name
        self.vector_store = ChromaVectorStore(
            client=self.client,
            collection_name=self.collection_name,
            embedding_function=GOOGLE_GEN_AI_EMBEDDING(),
        )


    def add_documents(self, collection_name, chunks) -> bool:
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
        