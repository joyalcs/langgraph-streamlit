from langchain_core.tools import tool
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter
import json
import os

def extract_pdf(file_path: str) -> str:
    """
    Extracts raw text from a PDF file.
    
    Args:
        file_path (str): The path to the PDF file.
        
    Returns:        
        str: JSON string containing the extracted text and metadata.
    """
    try:
        print(f"Extracting text from PDF: {file_path}")
        loader = PyPDFLoader(file_path)
        pages = loader.load()
        
        # Combine text from all pages
        full_text = "\n\n".join([page.page_content for page in pages])
        print("✓ PDF text extraction successful", full_text[:100], "...")
        return json.dumps({
            "status": "success",
            "text": full_text,
            "page_count": len(pages),
            "metadata": {"source": file_path}
        })
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})

def convert_to_md(text_json: str) -> str:
    """
    Converts extracted text to Markdown format (heuristic based).
    For now, this is a placeholder that assumes the text is already somewhat structured 
    or just passes it through. In a real scenario, this might use an LLM or complex regex.
    
    Args:
        text_json (str): JSON string from extract_pdf.
        
    Returns:
        str: JSON string with markdown text.
    """
    try:
        data = json.loads(text_json)
        text = data.get("text", "")
        
        # Simple heuristic: Try to identify headers based on capitalization and length
        # This is a basic implementation.
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
        
        return json.dumps({
            "status": "success",
            "markdown": md_text,
            "metadata": data.get("metadata", {})
        })
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})

def structure_split(markdown_json: str) -> str:
    """
    Splits markdown text by headers (Content-Based Chunking).
    
    Args:
        markdown_json (str): JSON string from convert_to_md.
        
    Returns:
        str: JSON string with splits.
    """
    try:
        data = json.loads(markdown_json)
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
            
        return json.dumps({
            "status": "success",
            "splits": splits_data,
            "count": len(splits_data)
        })
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})

def final_chunk(splits_json: str) -> str:
    """
    Creates final overlapping chunks from structural splits for embedding.
    
    Args:
        splits_json (str): JSON string from structure_split.
        
    Returns:
        str: JSON string with final chunks.
    """
    try:
        data = json.loads(splits_json)
        splits_data = data.get("splits", [])
        
        # Convert back to documents
        from langchain_core.documents import Document
        documents = [Document(page_content=s["page_content"], metadata=s["metadata"]) for s in splits_data]
        
        # Recursive split for chunk size control
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        final_splits = text_splitter.split_documents(documents)
        
        # Serialize
        final_chunks = []
        for split in final_splits:
            final_chunks.append({
                "page_content": split.page_content,
                "metadata": split.metadata
            })
            
        return json.dumps({
            "status": "success",
            "chunks": final_chunks,
            "total_chunks": len(final_chunks)
        })
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})
