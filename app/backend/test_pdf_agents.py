"""
Simple test script to diagnose PDF agent issues
"""
import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_validation_agent():
    """Test the PDF validation agent"""
    print("=" * 60)
    print("Testing PDF Validation Agent")
    print("=" * 60)
    
    from app.backend.agents.pdf_agents.pdf_validation_agent import pdf_validation_agent
    from app.backend.core.state import State
    
    # You need to replace this with an actual PDF file path on your system
    test_pdf = r"C:\path\to\your\test.pdf"  # CHANGE THIS
    
    if not os.path.exists(test_pdf):
        print(f"❌ Test PDF not found: {test_pdf}")
        print("Please update the test_pdf path in this script")
        return False
    
    state = State(file_path=test_pdf)
    
    try:
        result_state = pdf_validation_agent(state)
        print("\n✅ Validation agent completed!")
        print(f"Status: {result_state.get('pdf_validation_status')}")
        return True
    except Exception as e:
        print(f"\n❌ Validation agent failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_chunking_agent():
    """Test the PDF chunking agent"""
    print("\n" + "=" * 60)
    print("Testing PDF Chunking Agent")
    print("=" * 60)
    
    from app.backend.agents.pdf_agents.pdf_chunking_agent import pdf_chunking_agent
    from app.backend.core.state import State
    
    # You need to replace this with an actual PDF file path on your system
    test_pdf = r"C:\path\to\your\test.pdf"  # CHANGE THIS
    
    if not os.path.exists(test_pdf):
        print(f"❌ Test PDF not found: {test_pdf}")
        print("Please update the test_pdf path in this script")
        return False
    
    state = State(file_path=test_pdf)
    
    try:
        result_state = pdf_chunking_agent(state)
        print("\n✅ Chunking agent completed!")
        print(f"Status: {result_state.get('chunking_status')}")
        print(f"Total chunks: {result_state.get('total_chunks', 0)}")
        return True
    except Exception as e:
        print(f"\n❌ Chunking agent failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_tools_directly():
    """Test the tools directly without agents"""
    print("\n" + "=" * 60)
    print("Testing Tools Directly")
    print("=" * 60)
    
    from app.backend.tools.pdf_tools import validate_pdf_tool
    from app.backend.tools.chunking_tools import extract_pdf
    
    test_pdf = r"C:\path\to\your\test.pdf"  # CHANGE THIS
    
    if not os.path.exists(test_pdf):
        print(f"❌ Test PDF not found: {test_pdf}")
        print("Please update the test_pdf path in this script")
        return False
    
    try:
        print("\n1. Testing validate_pdf_tool...")
        result = validate_pdf_tool.invoke({"file_path": test_pdf})
        print(f"✅ Validation tool works! Status: {result.get('validation_status')}")
        
        print("\n2. Testing extract_pdf...")
        result = extract_pdf.invoke({"file_path": test_pdf})
        print(f"✅ Extract tool works! Response length: {len(result)}")
        
        return True
    except Exception as e:
        print(f"\n❌ Tool test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("PDF Agent Diagnostic Test")
    print("=" * 60)
    print("\n⚠️  IMPORTANT: Update the test_pdf path in this script first!\n")
    
    # Test tools first (simpler, no LLM involved)
    print("\n🔧 Step 1: Testing tools directly (no LLM)...")
    tools_ok = test_tools_directly()
    
    if not tools_ok:
        print("\n❌ Tools failed. Fix tool issues before testing agents.")
        sys.exit(1)
    
    # Test agents (requires LLM)
    print("\n🤖 Step 2: Testing agents (with LLM)...")
    
    # Test validation first (simpler, one tool)
    validation_ok = test_validation_agent()
    
    # Test chunking (more complex, four tools)
    chunking_ok = test_chunking_agent()
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Tools Direct: {'✅ PASSED' if tools_ok else '❌ FAILED'}")
    print(f"Validation Agent: {'✅ PASSED' if validation_ok else '❌ FAILED'}")
    print(f"Chunking Agent: {'✅ PASSED' if chunking_ok else '❌ FAILED'}")
    print("=" * 60)
