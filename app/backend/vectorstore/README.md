# Vector Database Storage

This directory stores FAISS vector databases containing embedded PDF chunks.

## Structure

Each collection is stored in its own subdirectory:
```
vectorstore/
├── pdf_chunks/          # Default collection
│   ├── index.faiss      # FAISS index file
│   └── index.pkl        # Metadata and document mapping
└── other_collection/    # Custom collections
    ├── index.faiss
    └── index.pkl
```

## Usage

Vector databases are created and managed by the embedding agent.

**Note:** This directory is ignored by git (listed in .gitignore) as vector databases can be large and should be regenerated as needed.
