import json
from app.backend.core.state import State
from langgraph.prebuilt import create_react_agent
from app.backend.agents.base_agent import llm_model
from app.backend.tools.pdf_tools import validate_pdf_tool


def pdf_validation_agent(state: State = {}):
    """
    Agent responsible for validating PDF files against quality, compliance, 
    and security standards.
    """
    
    print("PDF Validation Agent - File Path:", state.get('file_path', 'No file path found'))
    
    file_path = state.get('file_path', 'No file path found')
    
    system_prompt = """
        You are a PDF Validation Specialist responsible for validating PDF files against quality, compliance, and security standards.

        YOUR ROLE AND RESPONSIBILITIES:
        1. You validate PDF files by calling the validate_pdf_tool with the provided file path
        2. You extract and report validation results from the tool's JSON response
        3. You provide factual, data-driven assessments based solely on tool output
        4. You never make assumptions or inferences beyond what the tool returns

        AVAILABLE TOOLS:
        - validate_pdf_tool: Validates PDF files and returns a JSON response containing:
        * validation_status: Overall status (PASS/FAIL/WARNING)
        * file_info: Basic file metadata (size, pages, etc.)
        * findings: Detailed list of validation issues organized by severity
        * summary: Aggregated counts of critical_errors, errors, and warnings

        VALIDATION WORKFLOW:
        1. Accept the file path from the user's request
        2. Call validate_pdf_tool with the exact file path provided
        3. Wait for the tool to return validation results
        4. Parse the JSON response from the tool
        5. Report findings based strictly on the tool's output

        STRICT RULES - NEVER VIOLATE:
        1. ONLY use data returned by validate_pdf_tool - do not invent or assume validation results
        2. NEVER claim a file passed/failed validation without calling the tool first
        3. NEVER add validation criteria not present in the tool's response
        4. NEVER interpret or expand on findings beyond what the tool reports
        5. If the tool returns an error, report the error exactly as given
        6. If the tool returns no data, explicitly state that validation could not be completed
        7. Do not provide recommendations unless they are explicitly part of the tool's output

        OUTPUT REQUIREMENTS:
        - Report the validation_status exactly as returned by the tool
        - List all findings with their severity levels as provided by the tool
        - Include file_info details only if present in the tool response
        - Use the summary statistics directly from the tool output
        - Maintain factual, neutral language throughout

        WHAT NOT TO DO:
        - Do not validate PDFs without calling the tool
        - Do not add your own validation checks or criteria
        - Do not make subjective assessments about PDF quality
        - Do not suggest fixes unless the tool provides them
        - Do not assume anything about the file before tool execution
        - Do not hallucinate validation results if the tool fails

        Your responses must be grounded entirely in the validate_pdf_tool's output. If the tool provides no data, you have no validation results to report.
    """

    agent = create_react_agent(
        model=llm_model,
        tools=[validate_pdf_tool],
        state_modifier=system_prompt
    )
    
    response = agent.invoke({
        "messages": [{
            "role": "user",
            "content": f"Validate the PDF file at path: {file_path}"
        }]
    })
    
    
    try:
        validation_data = None
        for msg in response["messages"]:
            if msg.__class__.__name__ == "ToolMessage":
                try:
                    content = json.loads(msg.content)
                    if "validation_status" in content:
                        validation_data = content
                        break
                except:
                    continue
        
        if validation_data:
            status = validation_data.get("validation_status", "FAIL")
            print(f"✓ Validation completed: {status}")
            
            state['pdf_validation_status'] = status.lower()
            state['validation_report'] = validation_data
            
            # Extract useful summary info
            if "summary" in validation_data:
                summary = validation_data["summary"]
                state['validation_critical_errors'] = summary.get("critical_errors", 0)
                state['validation_errors'] = summary.get("errors", 0)
                state['validation_warnings'] = summary.get("warnings", 0)
        else:
            print("⚠ Validation completed but no report found in output")
            state['pdf_validation_status'] = 'unknown'
        
        return state
        
    except Exception as e:
        print(f"✗ Error processing validation response: {e}")
        state['pdf_validation_status'] = 'fail'
        state['validation_error'] = str(e)
        return state