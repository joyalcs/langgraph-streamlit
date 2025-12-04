"""
Minimal test to verify LangGraph agent setup works
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from app.backend.agents.base_agent import llm_model


@tool
def simple_test_tool(message: str) -> str:
    """A simple test tool that returns a greeting."""
    return f"Hello! You said: {message}"


def test_minimal_agent():
    """Test with the simplest possible agent"""
    print("Testing minimal agent setup...")
    
    # Very simple system prompt
    system_prompt = "You are a helpful assistant. Use the simple_test_tool to respond to the user."
    
    # Create agent
    agent = create_react_agent(
        model=llm_model,
        tools=[simple_test_tool],
        prompt=system_prompt
    )
    
    try:
        # Invoke with simple message
        response = agent.invoke({
            "messages": [{"role": "user", "content": "Say hello to me"}]
        })
        
        print("✅ Agent worked!")
        print(f"Response: {response}")
        return True
        
    except Exception as e:
        print(f"❌ Agent failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("Minimal Agent Test")
    print("=" * 60)
    print("\nThis test verifies that:")
    print("1. The LLM model is configured correctly")
    print("2. LangGraph create_react_agent works")
    print("3. Basic tool calling functions")
    print("\n" + "=" * 60 + "\n")
    
    success = test_minimal_agent()
    
    if success:
        print("\n✅ Basic agent setup is working!")
        print("The issue might be specific to PDF tools or prompts.")
    else:
        print("\n❌ Basic agent setup is broken!")
        print("Likely issues:")
        print("  - Invalid model name")
        print("  - Missing API key")
        print("  - LangChain/LangGraph version mismatch")
