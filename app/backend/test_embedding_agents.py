"""
Test script for embedding and vectoring agents
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.backend.agents.pdf_agents.embedding_agent import embedding_agent
from app.backend.agents.pdf_agents.retrieval_agent import retrieval_agent
from app.backend.core.state import State


def test_embedding_agent():
    """Test the embedding agent with sample chunks"""
    print("=" * 60)
    print("Testing Embedding Agent")
    print("=" * 60)
    
    # Sample chunks (simulating output from chunking agent)
    sample_chunks = [
        {
            "page_content": "This is a test document about machine learning. It covers various topics including neural networks, deep learning, and artificial intelligence.",
            "metadata": {"page": 1, "Header 1": "Introduction"}
        },
        {
            "page_content": "Neural networks are computational models inspired by biological neural networks. They consist of interconnected nodes organized in layers.",
            "metadata": {"page": 2, "Header 1": "Neural Networks"}
        },
        {
            "page_content": "Deep learning is a subset of machine learning that uses multi-layer neural networks. It has revolutionized computer vision and natural language processing.",
            "metadata": {"page": 3, "Header 1": "Deep Learning"}
        }
    ]
    
    state = State(
        pdf_chunks=sample_chunks,
        collection_name="test_collection"
    )
    
    try:
        result_state = embedding_agent(state)
        print("\n✅ Embedding agent completed!")
        print(f"Status: {result_state.get('embedding_status')}")
        print(f"Documents stored: {result_state.get('document_count')}")
        if result_state.get('vectorstore_info'):
            print(f"Save path: {result_state['vectorstore_info']['save_path']}")
        return True
    except Exception as e:
        print(f"\n❌ Embedding agent failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_retrieval_agent():
    """Test the retrieval agent"""
    print("\n" + "=" * 60)
    print("Testing Retrieval Agent")
    print("=" * 60)
    
    state = State(
        query="What is deep learning?",
        collection_name="test_collection",
        top_k=2
    )
    
    try:
        result_state = retrieval_agent(state)
        print("\n✅ Retrieval agent completed!")
        print(f"Status: {result_state.get('retrieval_status')}")
        print(f"Results found: {result_state.get('result_count')}")
        
        if result_state.get('search_results'):
            print("\nTop Results:")
            for i, result in enumerate(result_state['search_results'][:2], 1):
                print(f"\n{i}. Score: {result['similarity_score']:.4f}")
                print(f"   Content: {result['content'][:100]}...")
        
        return True
    except Exception as e:
        print(f"\n❌ Retrieval agent failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("Embedding & Retrieval Agent Test")
    print("=" * 60)
    print("\n⚠️  REQUIREMENTS:")
    print("1. OpenAI API key must be set (OPENAI_API_KEY)")
    print("2. faiss-cpu must be installed: pip install faiss-cpu")
    print("\n" + "=" * 60 + "\n")
    
    # Test embedding first
    embedding_ok = test_embedding_agent()
    
    if not embedding_ok:
        print("\n❌ Embedding test failed. Fix embedding issues before testing retrieval.")
        sys.exit(1)
    
    # Test retrieval
    retrieval_ok = test_retrieval_agent()
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Embedding Agent: {'✅ PASSED' if embedding_ok else '❌ FAILED'}")
    print(f"Retrieval Agent: {'✅ PASSED' if retrieval_ok else '❌ FAILED'}")
    print("=" * 60)
    
    if embedding_ok and retrieval_ok:
        print("\n🎉 All tests passed! Your embedding system is working!")
    else:
        print("\n⚠️  Some tests failed. Check the errors above.")
