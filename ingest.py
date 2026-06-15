import os
import chromadb
from chromadb.utils import embedding_functions

def chunk_text(text: str, chunk_size: int = 400, overlap: int = 50) -> list:
    """Splits text into fixed-size character chunks with a sliding window overlap."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start += (chunk_size - overlap)
        if start >= len(text):
            break
    return chunks

def run_ingestion_pipeline():
    # Point directly to your documents subfolder
    docs_dir = "./documents" 
    
    # 1. Initialize local persistent ChromaDB client
    chroma_client = chromadb.PersistentClient(path="./chroma_db")
    
    # 2. Set up the local sentence-transformers embedding function
    model_name = "all-MiniLM-L6-v2"
    embedding_func = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=model_name)
    
    # 3. Create or get the collection
    collection = chroma_client.get_or_create_collection(
        name="umd_professor_reviews",
        embedding_function=embedding_func
    )
    
    # Read all files inside that documents folder that end in .txt
    files = sorted([f for f in os.listdir(docs_dir) if f.endswith(".txt")])
    print(f"Found {len(files)} source documents.\n")
    
    all_chunks = []
    all_metadata = []
    all_ids = []
    chunk_counter = 0
    
    for file_name in files:
        file_path = os.path.join(docs_dir, file_name)
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read().strip()
        
        # Extract chunks using our sliding window
        chunks = chunk_text(content, chunk_size=400, overlap=50)
        
        for i, chunk_text_content in enumerate(chunks):
            all_chunks.append(chunk_text_content)
            
            all_metadata.append({
                "source": file_name,
                "chunk_index": i
            })
            
            all_ids.append(f"id_{chunk_counter}")
            chunk_counter += 1

    # 4. Upsert chunks and embeddings into ChromaDB
    print(f"Embedding and indexing {len(all_chunks)} chunks into ChromaDB... (This may take a moment)")
    collection.upsert(
        documents=all_chunks,
        metadatas=all_metadata,
        ids=all_ids
    )
    
    print("\n Success! Vector store populated.")
    print(f"Total items in database collection: {collection.count()}")

if __name__ == "__main__":
    run_ingestion_pipeline()