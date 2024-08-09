import os

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader, PyPDFLoader


# Use this link to learn how to test CustomDocumentLoader
# https://python.langchain.com/v0.1/docs/modules/data_connection/document_loaders/custom/#test-

def load_documents(file_path):
    ext = os.path.splitext(file_path)[-1].lower()
    if ext == ".pdf":
        document_loader = PyPDFLoader(file_path)
    elif ext == ".txt":
        document_loader = TextLoader(file_path)
    # elif ext == ".html":
    #     document_loader = UnstructuredHTMLLoader(file_path)
    else:
        raise ValueError(f"Unsupported file extension: {ext}")
    return document_loader.load()

def split_documents(documents: list[Document]):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=80,
        length_function=len,
        is_separator_regex=False,
    )
    return text_splitter.split_documents(documents)

def calculate_chunk_ids(chunks):

    # This will create IDs like "data/monopoly.pdf:6:2"
    # Page Source : Page Number : Chunk Index

    last_page_id = None
    current_chunk_index = 0

    for chunk in chunks:
        source = chunk.metadata.get("source")
        page = chunk.metadata.get("page")
        current_page_id = f"{source}:{page}"

        # If the page ID is the same as the last one, increment the index.
        if current_page_id == last_page_id:
            current_chunk_index += 1
        else:
            current_chunk_index = 0

        # Calculate the chunk ID.
        chunk_id = f"{current_page_id}:{current_chunk_index}"
        last_page_id = current_page_id

        # Add it to the page meta-data.
        chunk.metadata["id"] = chunk_id

    return chunks
