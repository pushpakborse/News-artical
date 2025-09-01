# News Article RAG System

A Retrieval-Augmented Generation system for news articles that scrapes, processes, and enables intelligent Q&A.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set your Gemini API key in `.env` file:
```
GEMINI_API_KEY=your_actual_api_key_here
```

3. Run the terminal interface:
```bash
python main.py
```

## Usage

### Terminal Interface
- System automatically loads news from major Indian news sources
- Ask questions directly in the terminal
- Get answers with source citations
- Type 'quit' to exit

### Programmatic Usage
```python
from rag_system import RAGSystem

rag = RAGSystem()
rag.load_news()
result = rag.query("What's the latest news?")
print(result['answer'])
```

## Features

- **Web Scraping**: Extracts titles and content from news URLs
- **Text Chunking**: Splits articles into 200-word chunks with 50-word overlap
- **Embeddings**: Uses sentence-transformers for semantic search
- **Vector Storage**: ChromaDB for persistent storage
- **RAG Pipeline**: Retrieves relevant chunks and generates answers
- **Source Citations**: Tracks and displays source URLs

## Files

- `scraper.py`: Web scraping functionality
- `embeddings.py`: Chunking, embeddings, and vector storage
- `rag_system.py`: Main RAG pipeline
- `main.py`: Terminal interface
- `example_usage.py`: Programmatic usage example