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
    
    # Create the agent with the validation tool (no system prompt parameter)
    agent = create_react_agent(
        model=llm_model,
        tools=[validate_pdf_tool]
    )
    
    # Invoke the agent with clear instructions in the user message
    response = agent.invoke({
        "messages": [{
            "role": "user",
            "content": f"You are a PDF validation specialist. Use validate_pdf_tool to validate this PDF file: {file_path}. The tool returns JSON with validation_status, file_info, and findings. Call the tool and report the results."
        }]
    })
    
    print("VALIDATION AGENT RESPONSE:", response)
    
    try:
        # Extract validation results from tool messages
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