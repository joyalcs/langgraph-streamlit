from langchain_core.tools import tool
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import MarkdownHeaderTextSplitter
from langchain_experimental.text_splitter import SemanticChunker
from langchain_openai import OpenAIEmbeddings
import json
import os
import tempfile
import uuid

def _save_to_temp_file(data: dict) -> str:
    """Helper to save data to a temp file and return the path."""
    temp_dir = tempfile.gettempdir()
    file_name = f"chunking_data_{uuid.uuid4()}.json"
    file_path = os.path.join(temp_dir, file_name)
    with open(file_path, 'w') as f:
        json.dump(data, f)
    return file_path

def _read_from_temp_file(file_path: str) -> dict:
    """Helper to read data from a temp file."""
    with open(file_path, 'r') as f:
        return json.load(f)

def extract_pdf(file_path: str) -> str:
    """
    Extracts raw text from a PDF file.
    
    Args:
        file_path (str): The path to the PDF file.
        
    Returns:        
        str: JSON string containing the status and path to the extracted text file.
    """
    try:
        print(f"Extracting text from PDF: {file_path}")
        loader = PyPDFLoader(file_path)
        pages = loader.load()
        
        # Combine text from all pages
        full_text = "\n\n".join([page.page_content for page in pages])
        print("✓ PDF text extraction successful")
        
        output_data = {
            "text": full_text,
            "page_count": len(pages),
            "metadata": {"source": file_path}
        }
        output_path = _save_to_temp_file(output_data)
        print(f"Extracted text saved to: {output_path}")
        return json.dumps({
            "status": "success",
            "file_path": output_path,
            "message": "Text extracted and saved to file."
        })
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})

def convert_to_md(input_json: str) -> str:
    """
    Converts extracted text to Markdown format (heuristic based).
    
    Args:
        input_json (str): JSON string from extract_pdf containing 'file_path'.
        
    Returns:
        str: JSON string with status and path to markdown file.
    """
    try:
        # Parse input to get file path
        input_data = json.loads(input_json)
        if "file_path" not in input_data:
            return json.dumps({"status": "error", "message": "No file_path provided in input"})
            
        # Read data from file
        data = _read_from_temp_file(input_data["file_path"])
        text = data.get("text", "")
        
        # Simple heuristic: Try to identify headers based on capitalization and length
        lines = text.split('\n')
        md_lines = []
        for line in lines:
            clean_line = line.strip()
            if not clean_line:
                md_lines.append("")
                continue
            
            # Assume short, all-caps lines are headers
            if len(clean_line) < 100 and clean_line.isupper():
                md_lines.append(f"## {clean_line}")
            else:
                md_lines.append(clean_line)
                
        md_text = "\n".join(md_lines)
        print("✓ Conversion to Markdown successful", md_text[:100])
        output_data = {
            "markdown": md_text,
            "metadata": data.get("metadata", {})
        }
        output_path = _save_to_temp_file(output_data)
        
        return json.dumps({
            "status": "success",
            "file_path": output_path,
            "message": "Markdown converted and saved to file."
        })
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})

def structure_split(input_json: str) -> str:
    """
    Splits markdown text by headers (Content-Based Chunking).
    
    Args:
        input_json (str): JSON string from convert_to_md containing 'file_path'.
        
    Returns:
        str: JSON string with status and path to splits file.
    """
    try:
        input_data = json.loads(input_json)
        if "file_path" not in input_data:
            return json.dumps({"status": "error", "message": "No file_path provided in input"})
            
        data = _read_from_temp_file(input_data["file_path"])
        markdown_text = data.get("markdown", "")
        
        headers_to_split_on = [
            ("#", "Header 1"),
            ("##", "Header 2"),
            ("###", "Header 3"),
        ]
        
        markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
        md_header_splits = markdown_splitter.split_text(markdown_text)
        
        # Serialize splits
        splits_data = []
        for split in md_header_splits:
            splits_data.append({
                "page_content": split.page_content,
                "metadata": split.metadata
            })
            
        output_data = {
            "splits": splits_data,
            "count": len(splits_data)
        }
        output_path = _save_to_temp_file(output_data)
            
        return json.dumps({
            "status": "success",
            "file_path": output_path,
            "message": "Structure split completed and saved to file."
        })
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})

def final_chunk(input_json: str) -> str:
    """
    Creates final overlapping chunks from structural splits for embedding.
    
    Args:
        input_json (str): JSON string from structure_split containing 'file_path'.
        
    Returns:
        str: JSON string with status and path to final chunks file.
    """
    try:
        input_data = json.loads(input_json)
        if "file_path" not in input_data:
            return json.dumps({"status": "error", "message": "No file_path provided in input"})
            
        data = _read_from_temp_file(input_data["file_path"])
        splits_data = data.get("splits", [])
        
        # Convert back to documents
        from langchain_core.documents import Document
        documents = [Document(page_content=s["page_content"], metadata=s["metadata"]) for s in splits_data]
        
        # Semantic split based on embedding similarity
        text_splitter = SemanticChunker(OpenAIEmbeddings())
        final_splits = text_splitter.split_documents(documents)
        
        # Serialize
        final_chunks = []
        for split in final_splits:
            final_chunks.append({
                "page_content": split.page_content,
                "metadata": split.metadata
            })
            
        output_data = {
            "chunks": final_chunks,
            "total_chunks": len(final_chunks)
        }
        output_path = _save_to_temp_file(output_data)
            
        return json.dumps({
            "status": "success",
            "file_path": output_path,
            "total_chunks": len(final_chunks),
            "message": "Final chunking completed and saved to file."
        })
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})
