from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import MarkdownHeaderTextSplitter
from langchain_core.tools import tool
import json


@tool
def extract_pdf(file_path: str) -> str:
    """Extract text content from the PDF and return JSON."""
    loader = PyPDFLoader(file_path)
    docs = loader.load()

    docs_data = [
        {"page_content": doc.page_content, "metadata": doc.metadata}
        for doc in docs
    ]

    print(f"✓ Extracted {len(docs)} pages")
    return json.dumps({"docs": docs_data})


@tool
def convert_to_md(docs_json: str) -> str:
    """Convert PDF extracted content to markdown."""
    data = json.loads(docs_json)
    docs = data.get("docs", [])

    md = ""
    for d in docs:
        category = d.get("metadata", {}).get("category", "")
        content = d.get("page_content", "")

        if "Title" in category:
            md += f"# {content}\n\n"
        elif "Header" in category:
            md += f"## {content}\n\n"
        elif "List" in category:
            md += f"- {content}\n"
        else:
            md += f"{content}\n\n"

    print("✓ Markdown created")
    return json.dumps({"markdown": md})


@tool
def structure_split(markdown_json: str) -> str:
    """Split markdown using header-aware splitting."""
    data = json.loads(markdown_json)
    markdown = data.get("markdown", "")

    # FIX: Correct argument name
    splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=[
            ("#", "Header 1"),
            ("##", "Header 2"),
            ("###", "Header 3"),
        ]
    )

    splits = splitter.split_text(markdown)

    splits_data = [
        {"page_content": s.page_content, "metadata": s.metadata}
        for s in splits
    ]

    print(f"✓ {len(splits)} structure splits generated")
    return json.dumps({"structure_splits": splits_data})


@tool
def final_chunk(splits_json: str, max_chunk_size: int = 3000) -> str:
    """Generate final embedding-ready chunks."""
    data = json.loads(splits_json)
    splits = data.get("structure_splits", [])

    final_chunks = []

    for s in splits:
        content = s.get("page_content", "")
        metadata = s.get("metadata", {})

        if len(content) <= max_chunk_size:
            final_chunks.append({"page_content": content, "metadata": metadata})
        else:
            paragraphs = content.split("\n\n")
            current = ""

            for para in paragraphs:
                if current and len(current) + len(para) + 2 > max_chunk_size:
                    final_chunks.append(
                        {"page_content": current.strip(), "metadata": metadata}
                    )
                    current = para
                else:
                    current += ("\n\n" if current else "") + para

            if current:
                final_chunks.append(
                    {"page_content": current.strip(), "metadata": metadata}
                )

    print(f"✓ Final chunks created: {len(final_chunks)}")
    return json.dumps({
        "chunks": final_chunks,
        "total_chunks": len(final_chunks)
    })