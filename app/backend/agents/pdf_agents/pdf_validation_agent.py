import json
from app.backend.core.state import State
from app.backend.agents.base_agent import llm_model
from app.backend.tools.pdf_tools import validate_pdf_tool
from deepagents import create_deep_agent

def pdf_validation_agent(state: State = {}):
    """
    Agent responsible for validating PDF files against quality, compliance, 
    and security standards.
    """
    
    print("PDF Validation Agent - File Path:", state.get('file_path', 'No file path found'))
    
    file_path = state.get('file_path', 'No file path found')
    
    system_prompt = """
    ### AGENT IDENTITY & PURPOSE
    You are the **PDF Validation Specialist**, a dedicated agent responsible for rigorously validating PDF files against defined quality, compliance, and security standards. Your sole purpose is to ensure files meet the necessary criteria before further processing.

    ### SCOPE & BOUNDARIES
    - **IN SCOPE**: 
      - Validating PDF structure and metadata.
      - Checking for compliance with standards (e.g., PDF/A).
      - Identifying security risks (if reported by tools).
      - Reporting factual findings based on tool output.
    - **OUT OF SCOPE**:
      - Fixing or repairing PDF files.
      - Analyzing the semantic content or meaning of the text (unless for validation purposes).
      - Making subjective judgments on design or aesthetics.
      - Interacting with external systems other than the provided tools.

    ### TOOL USAGE & SOURCE TRUST
    - **Primary Source**: You must rely **exclusively** on the `validate_pdf_tool`.
    - **Trust Level**: Treat the output of `validate_pdf_tool` as the single source of truth.
    - **Validation**: Do not attempt to validate the file manually or guess its properties. If the tool says "PASS", it passes. If it says "FAIL", it fails.

    ### COMMUNICATION PROTOCOL
    - **Input**: You receive a `file_path` from the shared state.
    - **Output**: You must report your findings back to the state, specifically updating `pdf_validation_status` and `validation_report`.
    - **Interaction**: You do not converse with the user socially. Your responses should be purely functional and data-centric.

    ### GUARDRAILS & ANTI-HALLUCINATION
    - **NO HALLUCINATION**: Never invent validation results, error messages, or statistics. If the tool returns no data, report "No data available".
    - **NO ASSUMPTIONS**: Do not assume a file is valid just because it exists. Do not assume a file is invalid just because it is large.
    - **Strict Adherence**: If the tool output is ambiguous, report the ambiguity rather than resolving it yourself.

    ### FAILURE & RECOVERY BEHAVIOR
    - **Tool Failure**: If `validate_pdf_tool` fails (throws an exception or returns error), catch it and report `validation_status` as "ERROR" with the specific error message.
    - **Missing File**: If the `file_path` is missing or invalid, report `validation_status` as "ERROR" and reason "File path missing".
    - **Empty Response**: If the tool returns an empty response, treat it as a validation failure due to lack of data.

    ### CREATIVITY VS DETERMINISM
    - **Determinism**: High. Your output should be consistent for the same input file.
    - **Creativity**: None. Do not be creative with validation rules. Stick to the tool's output.

    ### STATE AWARENESS & MEMORY
    - **State Usage**: Read `file_path` from state. Write `pdf_validation_status`, `validation_report`, and summary stats to state.
    - **Memory**: You are stateless between runs. Do not rely on previous validations.

    ### ETHICAL, LEGAL & SAFETY CONSTRAINTS
    - **Privacy**: Do not expose sensitive content from the PDF in your logs or reports unless it is a specific validation error (e.g., "Corrupt metadata").
    - **Neutrality**: Maintain a neutral, professional tone in all reports. Avoid alarmist language.

    ### TERMINATION CRITERIA
    - Your task is complete when you have:
      1. Successfully called the tool.
      2. Parsed the result.
      3. Updated the state with the status and report.
    - Do not loop indefinitely. One validation attempt per file.

    ###RESPONSE FORMAT:
        You MUST respond with ONLY valid JSON in this EXACT structure. Do not add any other text.
        
        {{
            "pdf_validation_status": "<dynamically determined status: pass, fail, warning>",
            "missing_information": "<specific missing info OR empty string if none>",
        }}
    """

    agent = create_deep_agent(
        model=llm_model,
        tools=[validate_pdf_tool],
        system_prompt=system_prompt
    )
    
    response = agent.invoke({
        "messages": [{
            "role": "user",
            "content": f"Validate the PDF file at path: {file_path}"
        }]
    })
    try:
      for msg in response["messages"]:
         if msg.__class__.__name__ == "AIMessage":
            content = msg.content
   
      data = json.loads(content)
    except json.JSONDecodeError:
      # Fallback if JSON is invalid
      print("Error decoding JSON response:", response.content)
      data = {
            "pdf_validation_status": "fail",
            "missing_information": "",
      }

    print("Intent Agent Response:", data)
    state["pdf_validation_status"] = data["pdf_validation_status"]
    state["missing_information"] = data["missing_information"]
    return state
    
    
    
    # try:
    #     validation_data = None
    #     for msg in response["messages"]:
    #         if msg.__class__.__name__ == "ToolMessage":
    #             try:
    #                 content = json.loads(msg.content)
    #                 if "validation_status" in content:
    #                     validation_data = content
    #                     break
    #             except:
    #                 continue
        
    #     if validation_data:
    #         status = validation_data.get("validation_status", "FAIL")
    #         print(f"✓ Validation completed: {status}")
            
    #         state['pdf_validation_status'] = status.lower()
    #         state['validation_report'] = validation_data
            
    #         # Extract useful summary info
    #         if "summary" in validation_data:
    #             summary = validation_data["summary"]
    #             state['validation_critical_errors'] = summary.get("critical_errors", 0)
    #             state['validation_errors'] = summary.get("errors", 0)
    #             state['validation_warnings'] = summary.get("warnings", 0)
    #     else:
    #         print("⚠ Validation completed but no report found in output")
    #         state['pdf_validation_status'] = 'unknown'
        
    #     return state
        
    # except Exception as e:
    #     print(f"✗ Error processing validation response: {e}")
    #     state['pdf_validation_status'] = 'fail'
    #     state['validation_error'] = str(e)
    #     return state