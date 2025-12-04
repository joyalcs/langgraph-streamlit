import json
from app.backend.core.state import State
from langgraph.prebuilt import create_react_agent
from app.backend.agents.base_agent import llm_model
from app.backend.tools.chunking_tools import extract_pdf, convert_to_md, structure_split, final_chunk


def pdf_chunking_agent(state: State = {}):
    """
    Agent responsible for extracting PDF content and creating structure-aware, 
    embedding-ready chunks suitable for vector search and RAG applications.
    """
    
    file_path = state.get('file_path', 'No file path found')
    
    # Create the agent with all chunking tools (no system prompt parameter)
    agent = create_react_agent(
        model=llm_model,
        tools=[extract_pdf, convert_to_md, structure_split, final_chunk]
    )
    
    # Invoke the agent with clear instructions in the user message
    response = agent.invoke({
        "messages": [{
            "role": "user", 
            "content": f"""You are a PDF chunking specialist. Process this PDF file: {file_path}

Use these 4 tools IN ORDER:
1. extract_pdf(file_path) - extract text from PDF, returns JSON with docs
2. convert_to_md(docs_json) - convert to markdown, pass the JSON from step 1
3. structure_split(markdown_json) - split by headers, pass the JSON from step 2  
4. final_chunk(splits_json, max_chunk_size=3000) - create final chunks, pass the JSON from step 3

Complete ALL 4 steps and report total chunks created."""
        }]
    })
    
    print("CHUNKING AGENT RESPONSE:", response)
    
    try:
        # Extract the final chunks from the tool messages
        chunks_data = None
        for msg in response["messages"]:
            if msg.__class__.__name__ == "ToolMessage":
                try:
                    content = json.loads(msg.content)
                    # Look for the final_chunk output
                    if "chunks" in content and "total_chunks" in content:
                        chunks_data = content
                except:
                    continue
        
        if chunks_data:
            print(f"✓ Successfully created {chunks_data['total_chunks']} chunks")
            state['pdf_chunks'] = chunks_data['chunks']
            state['chunking_status'] = 'success'
            state['total_chunks'] = chunks_data['total_chunks']
        else:
            print("⚠ Chunking completed but no final chunks found in output")
            state['chunking_status'] = 'partial'
        print("state", state)
        return state
        
    except Exception as e:
        print(f"✗ Error processing chunking response: {e}")
        state['chunking_status'] = 'fail'
        state['error_message'] = str(e)
        return state