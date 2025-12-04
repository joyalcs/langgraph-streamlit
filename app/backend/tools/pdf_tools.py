from langchain_core.tools import tool
from pypdf import PdfReader
import os
import datetime

@tool
def validate_pdf_tool(file_path: str) -> dict:
    """
    Validates a PDF file by checking its structure, metadata, and basic compliance.
    
    Args:
        file_path (str): The absolute path to the PDF file.
        
    Returns:
        dict: A dictionary containing validation results including file info, metadata, and any findings.
    """
    if not os.path.exists(file_path):
        return {"error": f"File not found: {file_path}"}

    try:
        reader = PdfReader(file_path)
        
        # File Info
        file_stats = os.stat(file_path)
        file_info = {
            "filename": os.path.basename(file_path),
            "size_bytes": file_stats.st_size,
            "pdf_version": str(reader.pdf_header),
            "page_count": len(reader.pages),
            "created_date": datetime.datetime.fromtimestamp(file_stats.st_ctime).isoformat(),
            "modified_date": datetime.datetime.fromtimestamp(file_stats.st_mtime).isoformat()
        }

        # Metadata
        meta = reader.metadata
        metadata = {}
        if meta:
            metadata = {
                "title": meta.title,
                "author": meta.author,
                "subject": meta.subject,
                "producer": meta.producer,
                "creator": meta.creator
            }

        # Findings & Compliance
        findings = []
        compliance = {
            "pdf_a": "NOT_CHECKED",
            "pdf_x": "NOT_CHECKED",
            "pdf_ua": "NOT_CHECKED"
        }

        # Basic Checks
        if reader.is_encrypted:
            findings.append({
                "severity": "INFO",
                "category": "SECURITY",
                "code": "ENCRYPTED",
                "message": "The PDF is encrypted.",
                "location": "Document Level",
                "recommendation": "Ensure you have the password if content extraction is needed."
            })

        # Check for PDF/A (Basic check via XMP or Metadata)
        # This is a heuristic check as full PDF/A validation is complex
        try:
            xmp = reader.xmp_metadata
            if xmp:
                # Simple check for PDF/A schema in XMP
                # Note: pypdf's xmp_metadata might need specific handling or might be None
                pass 
        except Exception:
            pass

        # Construct Report
        report = {
            "validation_status": "PASS", # Default to PASS, change if critical errors found
            "file_info": file_info,
            "summary": {
                "critical_errors": 0,
                "errors": 0,
                "warnings": 0,
                "info": len(findings)
            },
            "findings": findings,
            "compliance": compliance,
            "metadata": metadata
        }
        
        return report

    except Exception as e:
        return {
            "validation_status": "FAIL",
            "error": str(e),
            "findings": [{
                "severity": "CRITICAL",
                "category": "STRUCTURE",
                "code": "PARSE_ERROR",
                "message": f"Failed to parse PDF: {str(e)}",
                "location": "File",
                "recommendation": "Check if the file is a valid PDF."
            }]
        }
