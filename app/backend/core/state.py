from typing import Any, Dict, List, Optional, Literal
from langchain_core.documents import Document
from typing_extensions import TypedDict

class State(TypedDict):
    file_path: str
    file_name: str
    pdf_validation_status: Optional[Literal["pass", "fail", "warning"]]
    docs: List[Document]
    markdown: str
    structured_docs: List[Document]
    chunks: List[Document]
    missing_information: Optional[str]
