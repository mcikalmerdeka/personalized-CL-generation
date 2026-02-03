import os
from pathlib import Path
from typing import List
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document

from src.config.logging_config import setup_logger
from src.config.settings import CHUNK_SIZE, CHUNK_OVERLAP, EMBEDDING_MODEL, TOP_K_RESULTS

logger = setup_logger(__name__)


class VectorStoreManager:
    """Manages FAISS vector store for resume documents."""
    
    def __init__(self, embeddings_model: str = EMBEDDING_MODEL):
        """
        Initialize the vector store manager.
        
        Args:
            embeddings_model: OpenAI embeddings model name
        """
        self.embeddings = OpenAIEmbeddings(model=embeddings_model)
        self.vector_store = None
        logger.info(f"Initialized VectorStoreManager with embeddings model: {embeddings_model}")
    
    def load_and_index_resume(self, resume_path: str) -> None:
        """
        Load a resume PDF and create/update the FAISS vector store.
        
        Args:
            resume_path: Path to the resume PDF file
        """
        try:
            logger.info(f"Loading resume from: {resume_path}")
            
            # Load PDF
            loader = PyPDFLoader(resume_path)
            documents = loader.load()
            logger.info(f"Loaded {len(documents)} pages from resume")
            
            # Split into chunks
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=CHUNK_SIZE,
                chunk_overlap=CHUNK_OVERLAP
            )
            splits = text_splitter.split_documents(documents)
            logger.info(f"Split resume into {len(splits)} chunks")
            
            # Create or update vector store
            if self.vector_store is None:
                self.vector_store = FAISS.from_documents(splits, self.embeddings)
                logger.info("Created new FAISS vector store")
            else:
                self.vector_store.add_documents(splits)
                logger.info("Added documents to existing vector store")
                
        except Exception as e:
            logger.error(f"Error loading and indexing resume: {str(e)}")
            raise
    
    def save_vector_store(self, save_path: str) -> None:
        """
        Save the FAISS vector store to disk.
        
        Args:
            save_path: Directory path to save the vector store
        """
        if self.vector_store is None:
            logger.warning("No vector store to save")
            return
        
        try:
            Path(save_path).mkdir(parents=True, exist_ok=True)
            self.vector_store.save_local(save_path)
            logger.info(f"Saved vector store to: {save_path}")
        except Exception as e:
            logger.error(f"Error saving vector store: {str(e)}")
            raise
    
    def load_vector_store(self, load_path: str) -> None:
        """
        Load a FAISS vector store from disk.
        
        Args:
            load_path: Directory path containing the saved vector store
        """
        try:
            self.vector_store = FAISS.load_local(
                load_path, 
                self.embeddings,
                allow_dangerous_deserialization=True
            )
            logger.info(f"Loaded vector store from: {load_path}")
        except Exception as e:
            logger.error(f"Error loading vector store: {str(e)}")
            raise
    
    def search(self, query: str, k: int = TOP_K_RESULTS) -> List[Document]:
        """
        Search the vector store for relevant documents.
        
        Args:
            query: Search query (typically the job description)
            k: Number of top results to return
        
        Returns:
            List of relevant document chunks
        """
        if self.vector_store is None:
            logger.error("Vector store not initialized")
            raise ValueError("Vector store not initialized. Please load or create a vector store first.")
        
        try:
            results = self.vector_store.similarity_search(query, k=k)
            logger.info(f"Retrieved {len(results)} relevant documents")
            return results
        except Exception as e:
            logger.error(f"Error searching vector store: {str(e)}")
            raise
    
    def get_retriever(self, k: int = TOP_K_RESULTS):
        """
        Get a retriever for the vector store.
        
        Args:
            k: Number of top results to return
        
        Returns:
            Retriever object
        """
        if self.vector_store is None:
            logger.error("Vector store not initialized")
            raise ValueError("Vector store not initialized. Please load or create a vector store first.")
        
        return self.vector_store.as_retriever(search_kwargs={"k": k})
