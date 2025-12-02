from app.backend.workflows.pdf_graph import pdf_graph
from fastapi import FastAPI, UploadFile, File
import tempfile
import os

app = FastAPI()

@app.post("/")
async def run_graph(file: UploadFile = File(...)):
    # 1. Validate input
    if file.content_type != "application/pdf":
        return {"error": "Only PDF files are allowed"}

    # 2. Save to a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(await file.read())
        temp_path = tmp.name

    # 3. Pass to LangGraph
    try:
        result = await pdf_graph.ainvoke({
            "file_path": temp_path,
            "file_name": file.filename,
            # "content_type": file.content_type,
            # "file_size": file.size if hasattr(file, "size") else None
        })
    finally:
        # 4. Clean up temp file after processing
        os.remove(temp_path)

    return result
