import json
from app.backend.core.state import State
from app.backend.tools.embedding_tools import search_vectordb


def retrieval_agent(state: State = {}):
    """
    Agent responsible for searching the vector database to retrieve 
    relevant documents. This is a direct implementation (no LLM agent).
    """
    
    print("Retrieval Agent - Searching vector database...")
    
    # Get query and collection info from state
    query = state.get('query', state.get('user_query', ''))
    collection_name = state.get('collection_name', 'pdf_chunks')
    k = state.get('top_k', 5)
    
    if not query:
        print("⚠ No query provided")
        state['retrieval_status'] = 'fail'
        state['retrieval_error'] = 'No query provided'
        return state
    
    print(f"🔍 Query: {query}")
    print(f"📚 Collection: {collection_name}")
    
    try:
        # Perform search
        search_result = search_vectordb.invoke({
            "query": query,
            "collection_name": collection_name,
            "k": k
        })
        search_data = json.loads(search_result)
        
        if search_data.get("status") != "success":
            raise Exception(f"Search failed: {search_data.get('error', 'Unknown error')}")
        
        result_count = search_data['result_count']
        print(f"✅ Found {result_count} relevant documents")
        
        state['retrieval_status'] = 'success'
        state['search_results'] = search_data['results']
        state['result_count'] = result_count
        
        return state
        
    except Exception as e:
        print(f"✗ Error in retrieval process: {e}")
        state['retrieval_status'] = 'fail'
        state['retrieval_error'] = str(e)
        return state
