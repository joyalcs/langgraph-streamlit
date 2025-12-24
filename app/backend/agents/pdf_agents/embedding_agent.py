import json
from app.backend.core.state import State
from deepagents import create_deep_agent
from app.backend.agents.base_agent import llm_model
from app.backend.tools.chunking_tools import extract_pdf, convert_to_md, structure_split, final_chunk
from app.backend.tools.embedding_tools import create_embeddings, store_in_vectordb

def embedding_agent(state: State = {}):
    """
    Agent responsible for the end-to-end process of ingesting a PDF:
    Extraction -> Content-Based Chunking -> Embedding -> Vector Storage.
    """
    
    file_path = state.get('file_path', 'No file path found')
    collection_name = state.get('collection_name', 'pdf_chunks')
    
    system_prompt = """
    ### AGENT IDENTITY & PURPOSE
    You are the **Ingestion & Embedding Specialist**, a highly technical agent responsible for transforming raw PDF documents into searchable vector embeddings. You manage the full pipeline: extracting text, structuring it into meaningful chunks, creating embeddings, and storing them in a vector database.

    ### SCOPE & BOUNDARIES
    - **IN SCOPE**: 
      - Extracting text from PDF files.
      - Converting text to structured Markdown (content-based structuring).
      - Splitting content based on logical headers (Content-Based Chunking).
      - Creating vector embeddings for the chunks.
      - Storing embeddings in the vector database.
    - **OUT OF SCOPE**:
      - Answering user questions about the content.
      - Summarizing the document for the user (unless as a debug step).
      - Modifying the original PDF file.

    ### TOOL USAGE & WORKFLOW
    You must execute the following tools in a **STRICT SEQUENTIAL ORDER**. Do not skip steps.
    1. **extract_pdf(file_path)**: Get raw text.
    2. **convert_to_md(text_json)**: Structure text with headers.
    3. **structure_split(markdown_json)**: Split by headers (Content-Based Chunking).
    4. **final_chunk(splits_json)**: Prepare final overlapping chunks.
    5. **create_embeddings(chunks_json)**: Generate vectors.
    6. **store_in_vectordb(embeddings_json, collection_name)**: Save to DB.

    ### COMMUNICATION PROTOCOL
    - **Input**: You receive `file_path` and `collection_name`.
    - **Output**: You must update the state with `embedding_status` and `vectorstore_info`.
    - **Interaction**: This is a non-interactive process. Execute the pipeline and report status.

    ### GUARDRAILS & ANTI-HALLUCINATION
    - **NO DATA INVENTION**: Do not invent content. Use only what is extracted from the file.
    - **STRICT TOOLING**: Do not claim to have embedded data if the tools failed.
    - **VERIFICATION**: Check the output of each tool before proceeding to the next.

    ### SOURCE TRUST & VALIDATION
    - **Trust**: Trust the `extract_pdf` tool as the source of truth for document content.
    - **Validation**: If `extract_pdf` returns empty text, stop and report failure.

    ### OUTPUT QUALITY CONSTRAINTS
    - **Format**: Final output to state must be a status string ('success' or 'fail') and the vectorstore info dictionary.
    - **Completeness**: Ensure ALL chunks are processed.

    ### FAILURE & RECOVERY BEHAVIOR
    - **Tool Failure**: If a tool fails, stop immediately. Report the specific error message.
    - **Recovery**: No automatic retry logic is needed for this version. Fail fast.

    ### CREATIVITY VS DETERMINISM
    - **Determinism**: High. The pipeline should be reproducible.
    - **Creativity**: Zero. Do not alter the meaning of the text.

    ### STATE AWARENESS & MEMORY
    - **State Usage**: Read `file_path`. Write `pdf_chunks`, `embedding_status`, `vectorstore_info`.
    - **Memory**: Stateless between different files.

    ### ETHICAL, LEGAL & SAFETY CONSTRAINTS
    - **Privacy**: Process PII as is, without logging it to console unnecessarily.
    - **Integrity**: Do not inject external information into the embeddings.

    ### TERMINATION CRITERIA
    - Your task is complete when `store_in_vectordb` returns success.
    """
    
    agent = create_deep_agent(
        model=llm_model,
        tools=[create_embeddings, store_in_vectordb],
        system_prompt=system_prompt
    )
    
    print(f"🚀 Starting Embedding Agent Pipeline for: {file_path}")
    
    # create_react_agent expects a list of messages or a state with messages
    # We'll pass the user message to trigger the agent
    response = agent.invoke({
        "messages": [{
            "role": "user", 
            "content": f"Process the PDF at '{file_path}' and store in collection '{collection_name}'."
        }]
    })
    
    print("EMBEDDING AGENT RESPONSE:", response)
    
    # Parse response to update state
    # create_react_agent returns the final state. 
    # The state will contain the messages.
    # We need to find the last ToolMessage that contains our success info, or check the agent's final response.
    # However, since we want to extract specific fields like 'vectorstore_info', we should look at the tool outputs.
    
    try:
        vectorstore_info = None
        status = "fail"
        error = "Unknown error"
        
        # response['messages'] contains the conversation history
        for msg in response["messages"]:
            if msg.type == "tool": # LangChain message type check
                try:
                    content = json.loads(msg.content)
                    if "vectorstore_type" in content and content.get("status") == "success":
                        vectorstore_info = content
                        status = "success"
                    if content.get("status") == "error":
                        error = content.get("message")
                except:
                    continue
                    
        if status == "success" and vectorstore_info:
            print(f"✅ Pipeline completed successfully. Stored {vectorstore_info.get('document_count')} documents.")
            state['embedding_status'] = 'success'
            state['vectorstore_info'] = vectorstore_info
            state['collection_name'] = vectorstore_info.get('collection_name')
        else:
            print(f"❌ Pipeline failed: {error}")
            state['embedding_status'] = 'fail'
            state['embedding_error'] = error
            
        return state

    except Exception as e:
        print(f"❌ Critical Error in Embedding Agent: {e}")
        state['embedding_status'] = 'fail'
        state['embedding_error'] = str(e)
        return state
