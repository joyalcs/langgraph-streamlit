from langchain_core.tools import tool
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
import json
from typing import List


@tool
def create_embeddings(chunks_json: str) -> str:
    """
    Create vector embeddings from text chunks using OpenAI embeddings.
    
    Args:
        chunks_json (str): JSON string containing chunks with page_content and metadata.
        
    Returns:
        str: JSON with embedding info (count, dimension, status).
    """
    data = json.loads(chunks_json)
    chunks = data.get("chunks", [])
    
    if not chunks:
        return json.dumps({"error": "No chunks provided", "status": "fail"})
    
    # Convert to LangChain documents
    documents = [
        Document(page_content=chunk["page_content"], metadata=chunk["metadata"])
        for chunk in chunks
    ]
    
    # Initialize embeddings model
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    
    # Create embeddings (happens automatically when creating vectorstore)
    print(f"✓ Creating embeddings for {len(documents)} chunks...")
    
    # This will be passed to the vectorstore tool
    return json.dumps({
        "documents": chunks,  # Keep as serializable format
        "count": len(chunks),
        "embedding_model": "text-embedding-3-small",
        "status": "success"
    })


@tool
def store_in_vectordb(embeddings_json: str, collection_name: str = "pdf_chunks") -> str:
    """
    Store embedded documents in FAISS vector database.
    
    Args:
        embeddings_json (str): JSON from create_embeddings with documents.
        collection_name (str): Name for the vector collection.
        
    Returns:
        str: JSON with storage status and vector store info.
    """
    data = json.loads(embeddings_json)
    chunks = data.get("documents", [])
    
    if not chunks:
        return json.dumps({"error": "No documents to store", "status": "fail"})
    
    # Convert back to LangChain documents
    documents = [
        Document(page_content=chunk["page_content"], metadata=chunk["metadata"])
        for chunk in chunks
    ]
    
    # Initialize embeddings model
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    
    # Create FAISS vectorstore
    print(f"✓ Storing {len(documents)} documents in FAISS vector database...")
    vectorstore = FAISS.from_documents(documents, embeddings)
    
    # Save to disk
    save_path = f"./vectorstore/{collection_name}"
    vectorstore.save_local(save_path)
    
    print(f"✓ Vector database saved to: {save_path}")
    
    return json.dumps({
        "status": "success",
        "collection_name": collection_name,
        "document_count": len(documents),
        "save_path": save_path,
        "embedding_model": "text-embedding-3-small",
        "vectorstore_type": "FAISS"
    })


@tool
def search_vectordb(query: str, collection_name: str = "pdf_chunks", k: int = 5) -> str:
    """
    Search the vector database for relevant documents.
    
    Args:
        query (str): Search query text.
        collection_name (str): Name of the vector collection to search.
        k (int): Number of results to return (default: 5).
        
    Returns:
        str: JSON with search results.
    """
    try:
        # Load embeddings
        embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        
        # Load vectorstore
        load_path = f"./vectorstore/{collection_name}"
        vectorstore = FAISS.load_local(
            load_path, 
            embeddings,
            allow_dangerous_deserialization=True
        )
        
        # Perform similarity search
        print(f"🔍 Searching for: {query[:50]}...")
        results = vectorstore.similarity_search_with_score(query, k=k)
        
        # Format results
        search_results = []
        for doc, score in results:
            search_results.append({
                "content": doc.page_content,
                "metadata": doc.metadata,
                "similarity_score": float(score)
            })
        
        print(f"✓ Found {len(search_results)} relevant documents")
        
        return json.dumps({
            "status": "success",
            "query": query,
            "results": search_results,
            "result_count": len(search_results)
        })
        
    except Exception as e:
        return json.dumps({
            "status": "fail",
            "error": str(e),
            "message": f"Failed to search vectordb: {str(e)}"
        })
