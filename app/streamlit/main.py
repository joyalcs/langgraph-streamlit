import streamlit as st
import tempfile
import os
import uuid
import asyncio
import sys

# Ensure the root directory is in sys.path so we can import app.backend
# Assuming this script is run from the project root or app/streamlit
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../"))
if project_root not in sys.path:
    sys.path.append(project_root)

from app.backend.workflows.pdf_graph import pdf_graph

st.set_page_config(page_title="PDF Graph Streamlit", layout="wide")
st.title("PDF Graph Streamlit App 🦜🕸️")

# Initialize Thread ID
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

st.sidebar.text(f"Session Thread ID:\n{st.session_state.thread_id}")

st.write("Upload a PDF to process it through the LangGraph workflow.")

uploaded_file = st.file_uploader(
    "Upload PDF", accept_multiple_files=False, type="pdf"
)

async def process_file(file_content, file_name, thread_id):
    # Save to temp file as the graph expects a file path
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(file_content)
        temp_path = tmp.name

    try:
        config = {"configurable": {"thread_id": thread_id}}
        # Initial state
        initial_state = {
            "file_path": temp_path,
            "file_name": file_name,
        }
        
        # Invoke the graph
        result = await pdf_graph.ainvoke(initial_state, config=config)
        return result
    finally:
        # Cleanup temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)

if uploaded_file:
    if st.button("Process File"):
        with st.spinner("Processing through LangGraph..."):
            try:
                # Read file content once
                file_content = uploaded_file.read()
                
                # Run the async processing
                result = asyncio.run(process_file(file_content, uploaded_file.name, st.session_state.thread_id))
                
                st.success("Processing Complete!")
                
                # Display Results
                with st.expander("Full State Output", expanded=False):
                    st.json(result)
                
                # Show specific interesting parts if available
                if "pdf_validation_status" in result:
                    st.info(f"Validation Status: {result['pdf_validation_status']}")
                
                if "docs" in result:
                    st.write(f"Number of Documents: {len(result['docs'])}")
                    
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                st.exception(e)

# Chat Interface (Future extension)
if prompt := st.chat_input("Ask something about the processed PDF..."):
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        st.write("Chat functionality not yet connected to graph edges... (Update graph to support chat)")