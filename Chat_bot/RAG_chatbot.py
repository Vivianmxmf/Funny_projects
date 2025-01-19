import os
import requests
from typing import Dict, List, Optional
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import (
    PyPDFLoader,
    TextLoader,
    CSVLoader,
    JSONLoader
)
from langchain.chains import RetrievalQA
import chromadb
import pandas as pd

class RAGChatbot:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:5000",
        }
        
        # Vector store settings
        self.embeddings = None
        self.vector_store = None
        self.persist_directory = "vector_store"
        
        # Initialize conversation history
        self.conversation_history: List[Dict] = []
        
    def initialize_vector_store(self, persist_directory: Optional[str] = None):
        """Initialize vector store for document storage"""
        if persist_directory:
            self.persist_directory = persist_directory
            
        self.embeddings = OpenAIEmbeddings(openai_api_key=self.api_key)
        self.vector_store = Chroma(
            persist_directory=self.persist_directory,
            embedding_function=self.embeddings
        )
        
    def load_documents(self, file_paths: List[str]):
        """Load documents from various sources"""
        documents = []
        
        for file_path in file_paths:
            try:
                if file_path.endswith('.pdf'):
                    loader = PyPDFLoader(file_path)
                elif file_path.endswith('.txt'):
                    loader = TextLoader(file_path)
                elif file_path.endswith('.csv'):
                    loader = CSVLoader(file_path)
                elif file_path.endswith('.json'):
                    loader = JSONLoader(file_path)
                else:
                    print(f"Unsupported file type: {file_path}")
                    continue
                    
                documents.extend(loader.load())
                
            except Exception as e:
                print(f"Error loading {file_path}: {str(e)}")
                
        # Split documents into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        splits = text_splitter.split_documents(documents)
        
        # Add to vector store
        if not self.vector_store:
            self.initialize_vector_store()
        
        self.vector_store.add_documents(splits)
        print(f"Added {len(splits)} document chunks to vector store")
        
    def connect_to_database(self, connection_string: str):
        """
        Connect to external database
        Example connection strings:
        - PostgreSQL: postgresql://user:password@localhost:5432/dbname
        - MySQL: mysql://user:password@localhost:3306/dbname
        - SQLite: sqlite:///path/to/database.db
        """
        try:
            # Use SQLAlchemy to connect to database
            from sqlalchemy import create_engine
            engine = create_engine(connection_string)
            
            # Example: Load data from specific tables
            query = "SELECT * FROM your_table"
            df = pd.read_sql(query, engine)
            
            # Convert DataFrame to documents
            documents = []
            for _, row in df.iterrows():
                # Customize this based on your data structure
                content = " ".join(str(v) for v in row.values)
                documents.append({"content": content, "metadata": row.to_dict()})
                
            # Add to vector store
            if not self.vector_store:
                self.initialize_vector_store()
                
            self.vector_store.add_texts(
                texts=[doc["content"] for doc in documents],
                metadatas=[doc["metadata"] for doc in documents]
            )
            
            print(f"Added {len(documents)} database records to vector store")
            
        except Exception as e:
            print(f"Error connecting to database: {str(e)}")
            
    def chat(self, user_input: str, model: str = "anthropic/claude-2") -> str:
        """Process user input using RAG and get response"""
        try:
            # Retrieve relevant documents
            docs = self.vector_store.similarity_search(user_input, k=3)
            context = "\n".join([doc.page_content for doc in docs])
            
            # Prepare messages with context
            messages = [
                {"role": "system", "content": "You are a helpful AI assistant. Use the following context to answer questions, but also use your general knowledge when appropriate."},
                {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {user_input}"}
            ]
            
            # Prepare request
            data = {
                "model": model,
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 1000
            }
            
            # Make API call
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=data
            )
            response.raise_for_status()
            
            # Extract assistant's response
            result = response.json()
            return result['choices'][0]['message']['content']
            
        except Exception as e:
            return f"Error: {str(e)}"
            
    def clear_vector_store(self):
        """Clear all documents from vector store"""
        if self.vector_store:
            self.vector_store.delete_collection()
            self.vector_store = None

# Example usage
if __name__ == "__main__":
    api_key = "YOUR_OPENROUTER_API_KEY"
    chatbot = RAGChatbot(api_key)
    
    # Example: Load documents
    chatbot.load_documents([
        "path/to/document1.pdf",
        "path/to/document2.txt"
    ])
    
    # Example: Connect to database
    chatbot.connect_to_database(
        "postgresql://user:password@localhost:5432/dbname"
    )
    
    # Example conversation
    while True:
        user_input = input("You: ")
        if user_input.lower() in ['exit', 'quit']:
            break
            
        response = chatbot.chat(user_input)
        print(f"Assistant: {response}") 