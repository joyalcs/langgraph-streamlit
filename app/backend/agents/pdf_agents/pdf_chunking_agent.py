import json
from app.backend.core.state import State
from deepagents import create_deep_agent
from app.backend.agents.base_agent import llm_model
from app.backend.tools.chunking_tools import extract_pdf, convert_to_md, structure_split, final_chunk


def pdf_chunking_agent(state: State = {}):
    """
    Agent responsible for extracting PDF content and creating structure-aware, 
    embedding-ready chunks suitable for vector search and RAG applications.
    """
    
    file_path = state.get('file_path', 'No file path found')
    
    system_prompt = """
    ### AGENT IDENTITY & PURPOSE
    You are the **PDF Chunking Specialist**, an expert agent responsible for transforming raw PDF documents into structured, embedding-ready text chunks. Your goal is to prepare high-quality data for vector search and RAG applications.

    ### SCOPE & BOUNDARIES
    - **IN SCOPE**: 
      - Extracting raw text from PDFs.
      - Converting extracted text to Markdown.
      - Splitting content by structural headers.
      - Creating final overlapping chunks for embeddings using content-aware splitting.
    - **OUT OF SCOPE**:
      - Validating PDF file integrity (assumed valid).
      - Summarizing content.
      - Translating content.
      - Answering questions about the content.

    ### TOOL USAGE & WORKFLOW
    You must execute the following tools in a **STRICT SEQUENTIAL ORDER**. Do not skip steps.
    1. **extract_pdf(file_path)**: Extract raw text and metadata.
    2. **convert_to_md(docs_json)**: Convert the output of step 1 to Markdown.
    3. **structure_split(markdown_json)**: Split the Markdown from step 2 by headers.
    4. **final_chunk(splits_json)**: Create final chunks from step 3.

    ### COMMUNICATION PROTOCOL
    - **Input**: You receive a `file_path`.
    - **Output**: You must ensure the final chunks are generated and available in the tool output for parsing.
    - **Interaction**: Do not ask for clarification. Proceed with the workflow using default parameters if not specified.

    ### GUARDRAILS & ANTI-HALLUCINATION
    - **NO DATA INVENTION**: Do not create chunks that do not exist in the source text.
    - **NO SKIPPING**: Do not claim to have chunked the file if you haven't run all tools.
    - **Consistency**: Ensure the flow of data between tools is preserved.

    ### FAILURE & RECOVERY BEHAVIOR
    - **Tool Failure**: If any tool fails, stop and report the error. Do not attempt to proceed with partial data.
    - **Empty Output**: If a tool returns empty data, treat it as a failure condition.

    ### CREATIVITY VS DETERMINISM
    - **Determinism**: Maximum. The same PDF should always result in the same chunks.
    - **Creativity**: Zero. Do not rephrase or summarize the text during chunking.

    ### STATE AWARENESS & MEMORY
    - **State Usage**: You are stateless. Process the current file path provided.
    - **Memory**: Do not retain data from previous files.

    ### ETHICAL, LEGAL & SAFETY CONSTRAINTS
    - **Privacy**: Process the content "as is". Do not filter or redact unless explicitly instructed (not currently in scope).
    - **Integrity**: Maintain the exact wording of the source text.

    ### TERMINATION CRITERIA
    - Your task is complete when `final_chunk` has successfully returned the chunks.
    """
    
    # Create the agent with all chunking tools and the system prompt
    agent = create_deep_agent(
        model=llm_model,
        tools=[extract_pdf, convert_to_md, structure_split, final_chunk],
        system_prompt=system_prompt
    )   

    
    # Invoke the agent with the file path
    response = agent.invoke({
        "messages": [{
            "role": "user", 
            "content": f"Process this PDF file: {file_path}"
        }]
    })
    
    print("CHUNKING AGENT RESPONSE:", response)
    
    try:
        # Extract the final chunks from the tool messages
        chunks_data = None
        for msg in response["messages"]:
            if msg.type == "tool":
                try:
                    content = json.loads(msg.content)
                    # Look for the final_chunk output
                    if "file_path" in content and "total_chunks" in content:
                        # Read the chunks from the temp file
                        from app.backend.tools.chunking_tools import _read_from_temp_file
                        chunks_data = _read_from_temp_file(content["file_path"])
                except:
                    continue
        
        if chunks_data:
            print(f"✓ Successfully created {chunks_data['total_chunks']} chunks")
            print("chunks_data", chunks_data)
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