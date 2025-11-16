"""
Document Processor Service
Handles PDF extraction, text chunking, embedding, and storage.
"""

import os
from typing import Dict, Any, List
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from pypdf import PdfReader
from config import CHROMA_DB_DIR

class DocumentProcessor:
    def __init__(self):
        # Define embeddings model (you can replace with OpenAIEmbeddings or others)
        self.embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        self.vectorstore_path = CHROMA_DB_DIR # Updated path to match config.py

    def process_pdf(self, file_path: str, doc_id: str, filename: str, uploaded_by: str) -> Dict[str, Any]:
        """
        Extract text from PDF, split into chunks, generate embeddings, and store in Chroma.
        """
        # Step 1: Extract text
        text = self._extract_text_from_pdf(file_path)
        if not text.strip():
            raise ValueError("No readable text found in PDF")

        # Step 2: Split into chunks
        chunks = self._split_into_chunks(text)
        if not chunks:
            raise ValueError("Failed to split document into chunks")

        # Step 3: Generate embeddings and store in Chroma
        metadatas = [{"doc_id": doc_id, "filename": filename, "uploaded_by": uploaded_by}] * len(chunks)
        vectorstore = Chroma.from_texts(
            texts=chunks,
            embedding=self.embedding_model,
            metadatas=metadatas,
            persist_directory=self.vectorstore_path,
            collection_name="faculty_documents" # Use doc_id as collection name for isolation
        )
        vectorstore.persist()

        # Return summary info
        return {
            "document_id": doc_id,
            "filename": filename,
            "chunks_created": len(chunks),
            "stored_path": self.vectorstore_path
        }

    def _extract_text_from_pdf(self, file_path: str) -> str:
        """Extracts text content from each page of the PDF."""
        text = ""
        with open(file_path, "rb") as f:
            pdf = PdfReader(f)
            for page in pdf.pages:
                text += page.extract_text() or ""
        return text

    def _split_into_chunks(self, text: str) -> List[str]:
        """Splits text into manageable chunks for embedding."""
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        return splitter.split_text(text)
