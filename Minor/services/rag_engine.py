"""
RAG Engine Service
Handles retrieval-augmented generation for student queries
"""

from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_huggingface import HuggingFaceEndpoint
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from typing import Dict, List
import os
import logging
from config import CHROMA_DB_DIR

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RAGEngine:
    def __init__(self):
        self.chroma_path = CHROMA_DB_DIR
        self.embedding_model = "sentence-transformers/all-MiniLM-L6-v2"
        self.llm_model = "mistralai/Mistral-7B-Instruct-v0.2"
        
        self.embeddings = self._initialize_embeddings()
        self.vectorstore = self._initialize_vectorstore()
        self.llm = self._initialize_llm()
        
    def _initialize_embeddings(self):
        """Initialize embeddings model"""
        return HuggingFaceEmbeddings(
            model_name=self.embedding_model,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
    
    def _initialize_vectorstore(self):
        """Initialize ChromaDB connection"""
        return Chroma(
            collection_name="faculty_documents",
            embedding_function=self.embeddings,
            persist_directory=self.chroma_path
        )
    
    def _initialize_llm(self):
        """Initialize HuggingFace LLM"""
        api_token = os.getenv("HUGGINGFACEHUB_API_TOKEN")
        if not api_token:
            raise ValueError("HUGGINGFACEHUB_API_TOKEN not found in environment")
        
        return HuggingFaceEndpoint(
            repo_id=self.llm_model,
            temperature=0.3,
            max_new_tokens=1024,
            huggingfacehub_api_token=api_token
        )
    
    def answer_query(self, query: str) -> Dict:
        """
        Answer student query using RAG
        Standard Q&A mode
        """
        try:
            # Create retriever
            retriever = self.vectorstore.as_retriever(
                search_type="similarity",
                search_kwargs={"k": 5}
            )
            
            # Define prompt template
            prompt_template = """Use the following context to answer the question. 
If you don't know the answer based on the context, say so clearly.

Context: {context}

Question: {question}

Answer: Provide a clear, concise answer with examples where appropriate."""

            PROMPT = PromptTemplate(
                template=prompt_template,
                input_variables=["context", "question"]
            )
            
            # Create QA chain
            qa_chain = RetrievalQA.from_chain_type(
                llm=self.llm,
                chain_type="stuff",
                retriever=retriever,
                return_source_documents=True,
                chain_type_kwargs={"prompt": PROMPT}
            )
            
            # Get answer
            result = qa_chain({"query": query})
            
            # Extract sources
            sources = list(set([
                doc.metadata.get("source", "Unknown")
                for doc in result["source_documents"]
            ]))
            
            return {
                "answer": result["result"],
                "sources": sources,
                "mode": "qa"
            }
            
        except Exception as e:
            logger.error(f"Error in answer_query: {str(e)}")
            raise
    
    def generate_study_notes(self, topic: str) -> Dict:
        """
        Generate comprehensive study notes on a topic
        Enhanced formatting with structure
        """
        try:
            retriever = self.vectorstore.as_retriever(
                search_type="similarity",
                search_kwargs={"k": 7}
            )
            
            prompt_template = """Using the provided context, create detailed study notes on: {question}

Format your response as follows:

**KEY CONCEPTS:**
• [List main concepts with brief definitions]

**DETAILED EXPLANATION:**
[Provide comprehensive explanation with examples]

**IMPORTANT POINTS TO REMEMBER:**
• [Highlight critical information]

**PRACTICE QUESTIONS:**
1. [Conceptual question with answer]
2. [Application question with answer]
3. [Analysis question with answer]

Context: {context}

Generate comprehensive study notes now:"""

            PROMPT = PromptTemplate(
                template=prompt_template,
                input_variables=["context", "question"]
            )
            
            qa_chain = RetrievalQA.from_chain_type(
                llm=self.llm,
                chain_type="stuff",
                retriever=retriever,
                return_source_documents=True,
                chain_type_kwargs={"prompt": PROMPT}
            )
            
            result = qa_chain({"query": topic})
            
            sources = list(set([
                doc.metadata.get("source", "Unknown")
                for doc in result["source_documents"]
            ]))
            
            return {
                "answer": result["result"],
                "sources": sources,
                "mode": "notes"
            }
            
        except Exception as e:
            logger.error(f"Error in generate_study_notes: {str(e)}")
            raise
    
    def generate_practice_questions(self, topic: str) -> Dict:
        """
        Generate practice questions with answers
        Multiple formats: MCQ, Short Answer, Conceptual
        """
        try:
            retriever = self.vectorstore.as_retriever(
                search_type="similarity",
                search_kwargs={"k": 6}
            )
            
            prompt_template = """Based on the context provided, generate practice questions about: {question}

Create a mix of question types:

**MULTIPLE CHOICE QUESTIONS (3 questions):**
[Each with 4 options and correct answer marked]

**SHORT ANSWER QUESTIONS (3 questions):**
[With brief model answers]

**CONCEPTUAL QUESTIONS (2 questions):**
[Deeper understanding questions with detailed answers]

Context: {context}

Generate the practice questions now:"""

            PROMPT = PromptTemplate(
                template=prompt_template,
                input_variables=["context", "question"]
            )
            
            qa_chain = RetrievalQA.from_chain_type(
                llm=self.llm,
                chain_type="stuff",
                retriever=retriever,
                return_source_documents=True,
                chain_type_kwargs={"prompt": PROMPT}
            )
            
            result = qa_chain({"query": topic})
            
            sources = list(set([
                doc.metadata.get("source", "Unknown")
                for doc in result["source_documents"]
            ]))
            
            return {
                "answer": result["result"],
                "sources": sources,
                "mode": "practice"
            }
            
        except Exception as e:
            logger.error(f"Error in generate_practice_questions: {str(e)}")
            raise
    
    def get_documents_context(self, document_ids: List[str]) -> str:
        """
        Retrieve concatenated context from specific documents
        Used by faculty tools for content generation
        """
        try:
            all_chunks = []
            
            for doc_id in document_ids:
                results = self.vectorstore.get(
                    where={"document_id": doc_id},
                    include=["documents"]
                )
                
                if results and results['documents']:
                    all_chunks.extend(results['documents'])
            
            # Concatenate and limit to reasonable size
            context = "\n\n".join(all_chunks[:20])  # Limit to 20 chunks
            return context
            
        except Exception as e:
            logger.error(f"Error retrieving documents context: {str(e)}")
            return ""
    
    def check_vectorstore(self) -> str:
        """Health check for vector store"""
        try:
            count = self.vectorstore._collection.count()
            return f"operational ({count} chunks)"
        except:
            return "unavailable"
    
    def check_llm(self) -> str:
        """Health check for LLM"""
        try:
            # Simple test query
            test = self.llm.invoke("Hello")
            return "operational"
        except:
            return "unavailable"
    
    def delete_document(self, doc_id: str):
        """Delete document from vector store"""
        try:
            results = self.vectorstore.get(where={"document_id": doc_id})
            if results and results['ids']:
                self.vectorstore.delete(ids=results['ids'])
                logger.info(f"Deleted vectors for document {doc_id}")
        except Exception as e:
            logger.error(f"Error deleting document: {str(e)}")
            raise