import streamlit as st
st.title("Hello Streamlit 👋")
st.write("This is my first Streamlit app!")

uploaded_file = st.file_uploader(
    "Upload the pdf for storing the data", accept_multiple_files=False, type="pdf"
)
if uploaded_file:
    prompt = st.chat_input(
        "Say something", accept_file=True, file_type=["pdf"])
    if prompt:
        text = prompt.get("text")
        files = prompt.get("files")
        
        if text:
            st.write(f"User has sent the following prompt: {text}")
        
        if files:
            for file in files:
                st.write(f"File uploaded: {file.name}")
                pdf_bytes = file.read()
                st.write(f"PDF size: {len(pdf_bytes)} bytes")