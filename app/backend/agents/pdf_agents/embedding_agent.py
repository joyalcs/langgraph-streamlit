import json
from app.backend.core.state import State
from app.backend.tools.embedding_tools import create_embeddings, store_in_vectordb


def embedding_agent(state: State = {}):
    """
    Agent responsible for creating embeddings from PDF chunks and storing them
    in a vector database. This is a direct implementation (no LLM agent).
    """
    
    print("Embedding Agent - Processing chunks...")
    
    # Get chunks from state
    chunks = state.get('pdf_chunks', [])
    collection_name = state.get('collection_name', 'pdf_chunks')
    
    if not chunks:
        print("⚠ No chunks found in state")
        state['embedding_status'] = 'fail'
        state['embedding_error'] = 'No chunks provided'
        return state
    
    print(f"📊 Found {len(chunks)} chunks to embed")
    
    try:
        # Step 1: Create embeddings
        chunks_json = json.dumps({"chunks": chunks})
        embeddings_result = create_embeddings.invoke({"chunks_json": chunks_json})
        embeddings_data = json.loads(embeddings_result)
        
        if embeddings_data.get("status") != "success":
            raise Exception(f"Embedding creation failed: {embeddings_data.get('error', 'Unknown error')}")
        
        print(f"✓ Embeddings created for {embeddings_data['count']} chunks")
        
        # Step 2: Store in vector database
        vectorstore_result = store_in_vectordb.invoke({
            "embeddings_json": embeddings_result,
            "collection_name": collection_name
        })
        vectorstore_data = json.loads(vectorstore_result)
        
        if vectorstore_data.get("status") != "success":
            raise Exception(f"Vector storage failed: {vectorstore_data.get('error', 'Unknown error')}")
        
        print(f"✅ Successfully stored {vectorstore_data['document_count']} documents")
        print(f"   Collection: {vectorstore_data['collection_name']}")
        print(f"   Path: {vectorstore_data['save_path']}")
        
        state['embedding_status'] = 'success'
        state['vectorstore_info'] = vectorstore_data
        state['collection_name'] = vectorstore_data['collection_name']
        state['document_count'] = vectorstore_data['document_count']
        
        return state
        
    except Exception as e:
        print(f"✗ Error in embedding process: {e}")
        state['embedding_status'] = 'fail'
        state['embedding_error'] = str(e)
        return state
