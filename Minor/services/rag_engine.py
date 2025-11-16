"""
RAG Engine Service
Handles retrieval-augmented generation for student queries
"""
import os
import logging
from typing import Dict, List, Any

from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_chroma import Chroma
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings

from config import CHROMA_DB_DIR

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RAGEngine:
    def __init__(self):
        self.chroma_path = CHROMA_DB_DIR
        self.embedding_model = "sentence-transformers/all-MiniLM-L6-v2"
        
        self.embeddings = self._initialize_embeddings()
        self.vectorstore = self._initialize_vectorstore()
        self.llm = self._initialize_llm()
        
        self.store = {}  # To store chat histories for different sessions
        self.conversational_rag_chain = self._create_conversational_rag_chain()

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
        """Initialize Groq LLM"""
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in environment")
        
        return ChatGroq(groq_api_key=api_key, model_name="openai/gpt-oss-120b")

    def _create_conversational_rag_chain(self):
        """
        Creates the conversational RAG chain manually using LCEL.
        This version ensures the output is a dictionary containing 'answer' and 'context'.
        """
        retriever = self.vectorstore.as_retriever()

        # 1. Prompt and chain to reformulate the question based on history
        contextualize_q_system_prompt = (
            "Given a chat history and the latest user question "
            "which might reference context in the chat history, "
            "formulate a standalone question which can be understood "
            "without the chat history. Do NOT answer the question, "
            "just reformulate it if needed and otherwise return it as is."
        )
        contextualize_q_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", contextualize_q_system_prompt),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}"),
            ]
        )
        history_aware_query_chain = contextualize_q_prompt | self.llm | StrOutputParser()

        # 2. Prompt and chain for answering the question
        system_prompt = (
            "You are an assistant for question-answering tasks. "
            "Use the following pieces of retrieved context to answer "
            "the question. If you don't know the answer, say that you "
            "don't know. Use three sentences maximum and keep the "
            "answer concise."
            "\n\n"
            "{context}"
        )
        qa_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}"),
            ]
        )
        question_answer_chain = qa_prompt | self.llm | StrOutputParser()

        # 3. Chain to retrieve documents
        def get_docs(input_dict):
            query = history_aware_query_chain.invoke(input_dict)
            return retriever.invoke(query)

        # 4. Manually construct the full chain to return a dictionary
        rag_chain = (
            RunnablePassthrough.assign(context=get_docs)
            .assign(answer=question_answer_chain)
        )
        
        # 5. Wrap with history management
        return RunnableWithMessageHistory(
            rag_chain,
            self.get_session_history,
            input_messages_key="input",
            history_messages_key="chat_history",
            output_messages_key="answer",
        )

    def get_session_history(self, session_id: str) -> BaseChatMessageHistory:
        """Get chat history for a session"""
        if session_id not in self.store:
            self.store[session_id] = ChatMessageHistory()
        return self.store[session_id]

    async def answer_query(self, query: str, session_id: str) -> Dict:
        """
        Answer student query using conversational RAG.
        """
        try:
            response_dict = self.conversational_rag_chain.invoke(
                {"input": query},
                config={"configurable": {"session_id": session_id}},
            )

            sources = []
            if 'context' in response_dict and response_dict['context']:
                sources = list(set([
                    doc.metadata.get("source", "Unknown")
                    for doc in response_dict['context']
                ]))

            return {
                "answer": response_dict.get("answer", "Sorry, I encountered an issue and couldn't find an answer."),
                "sources": sources,
                "mode": "qa"
            }
            
        except Exception as e:
            logger.error(f"Error in answer_query: {str(e)}")
            raise

    def get_documents_context(self, document_ids: List[str]) -> str:
        """
        Retrieve concatenated context from specific documents.
        This implementation fetches all data and filters in Python to ensure robustness.
        """
        try:
            all_chunks = []
            # Fetch all data from the collection
            all_data = self.vectorstore._collection.get(include=["metadatas", "documents"])
            
            if not all_data['documents']:
                logger.warning("Vector store returned no documents.")
                return ""

            # Filter in Python
            for i, metadata in enumerate(all_data['metadatas']):
                if metadata and metadata.get('doc_id') in document_ids:
                    all_chunks.append(all_data['documents'][i])
            
            if not all_chunks:
                logger.warning(f"No chunks found for document IDs: {document_ids}. Total items checked: {len(all_data['documents'])}")

            # Concatenate and limit to reasonable size
            context = "\n\n".join(all_chunks[:20])
            return context
            
        except Exception as e:
            logger.error(f"Error retrieving documents context: {str(e)}")
            return ""

    def check_vectorstore(self) -> str:
        """Health check for vector store"""
        try:
            count = self.vectorstore._collection.count()
            return f"operational ({count} chunks)"
        except Exception as e:
            logger.error(f"Vectorstore check failed: {e}")
            return "unavailable"

    def check_llm(self) -> str:
        """Health check for LLM"""
        try:
            self.llm.invoke("Hello")
            return "operational"
        except Exception as e:
            logger.error(f"LLM check failed: {e}")
            return "unavailable"

    def delete_document(self, doc_id: str):
        """Delete document from vector store"""
        try:
            results = self.vectorstore.get(where={"doc_id": doc_id})
            if results and results['ids']:
                self.vectorstore.delete(ids=results['ids'])
                logger.info(f"Deleted vectors for document {doc_id}")
        except Exception as e:
            logger.error(f"Error deleting document: {str(e)}")
            raise