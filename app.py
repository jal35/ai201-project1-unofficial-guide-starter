"""
RAG (Retrieval-Augmented Generation) Application
Retrieves relevant professor reviews from ChromaDB and generates responses using Groq LLM
"""

import os
from dotenv import load_dotenv
import chromadb
from chromadb.utils import embedding_functions
from groq import Groq

# Load environment variables from .env file
load_dotenv("./.env/.env.example")
# ========================
# ChromaDB Setup
# ========================

def connect_to_chromadb():
    """
    Connect to the local ChromaDB instance and return the collection.
    Uses sentence-transformers 'all-MiniLM-L6-v2' for embeddings.
    """
    # Initialize ChromaDB client with local persistent storage
    client = chromadb.PersistentClient(path="./chroma_db")
    
    # Re-initialize the exact same embedding function used during ingestion
    model_name = "all-MiniLM-L6-v2"
    embedding_func = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=model_name)
    
    # Get the existing collection and bind the embedding function to it
    collection = client.get_collection(
        name="umd_professor_reviews",
        embedding_function=embedding_func
    )
    
    return collection


# ========================
# Retrieval Function
# ========================

def retrieve_documents(collection, query: str, k: int = 3) -> list:
    """
    Retrieve the top-k most relevant document chunks from the collection.
    """
    # Query the collection for top-k similar documents
    results = collection.query(
        query_texts=[query],
        n_results=k
    )
    
    # Format results for display
    retrieved_docs = []
    if results and results['documents'] and len(results['documents']) > 0:
        for i, doc in enumerate(results['documents'][0]):
            retrieved_docs.append({
                'index': i + 1,
                'content': doc,
                'distance': results['distances'][0][i] if results['distances'] else None,
                'metadata': results['metadatas'][0][i] if results['metadatas'] else {}
            })
    
    return retrieved_docs


# ========================
# Groq LLM Generation
# ========================

def generate_response(query: str, retrieved_docs: list) -> str:
    """
    Generate a response using Groq's llama-3.3-70b-versatile model.
    """
    # Retrieve API key from environment
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError(
            "GROQ_API_KEY not found in environment variables. "
            "Please set it in a .env file or as an environment variable."
        )
    
    # Initialize Groq client
    client = Groq(api_key=api_key)
    
    # Build context from retrieved documents
    context = "\n\n".join([
        f"Source {doc['index']} (File: {doc['metadata'].get('source', 'Unknown')}):\n{doc['content']}" 
        for doc in retrieved_docs
    ])
    
    # Create the prompt
    system_prompt = """You are a helpful assistant answering questions about UMD professors and courses.
Use the provided source documents to answer the user's question. If the documents don't contain relevant information, 
say so clearly. Always cite which source file(s) you used based on the metadata provided."""
    
    user_prompt = f"""Here are relevant documents about UMD courses:

{context}

User question: {query}

Please answer the question based on the documents provided."""
    
    # Corrected to Groq's OpenAI-compatible chat completion syntax
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        max_tokens=1024,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )
    
    return completion.choices[0].message.content


# ========================
# Main RAG Query Function
# ========================

def rag_query(collection, query: str) -> str:
    """
    Complete RAG pipeline: retrieve documents and generate response.
    """
    print(f"\n{'='*60}")
    print(f"Query: {query}")
    print(f"{'='*60}\n")
    
    # Step 1: Retrieve relevant documents
    print("📚 Retrieving relevant sources...\n")
    retrieved_docs = retrieve_documents(collection, query, k=3)
    
    if not retrieved_docs:
        print("⚠️  No relevant documents found in the collection.")
        return ""
    
    # Print retrieved sources for transparency
    for doc in retrieved_docs:
        print(f"--- Source {doc['index']} | File: {doc['metadata'].get('source', 'Unknown')} (Dist: {round(doc['distance'], 4) if doc['distance'] is not None else 'N/A'}) ---")
        print(doc['content'])
        print()
    
    # Step 2: Generate response using LLM
    print("🤖 Generating response...\n")
    response = generate_response(query, retrieved_docs)
    
    print("📝 Generated Answer:")
    print("-" * 60)
    print(response)
    print("-" * 60)
    
    return response


# ========================
# Main Entry Point
# ========================

def main():
    """
    Main function to run the RAG application with an interactive query loop.
    """
    try:
        # Connect to ChromaDB
        print("🔗 Connecting to ChromaDB...")
        collection = connect_to_chromadb()
        print("✅ Connected to collection: 'umd_professor_reviews'\n")
        
        # Interactive query loop
        while True:
            user_query = input("\n📖 Enter your question (or 'quit' to exit): ").strip()
            
            if user_query.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Goodbye!")
                break
            
            if not user_query:
                print("⚠️  Please enter a valid question.")
                continue
            
            try:
                rag_query(collection, user_query)
            except ValueError as e:
                print(f"\n❌ Error: {e}")
                break
            except Exception as e:
                print(f"\n❌ Error generating response: {e}")
                continue
    
    except Exception as e:
        print(f"❌ Error connecting to ChromaDB: {e}")
        print("Make sure ChromaDB is initialized at ./chroma_db")


if __name__ == "__main__":
    main()