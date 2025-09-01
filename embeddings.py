from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings
import uuid

class EmbeddingManager:
    def __init__(self, model_name="all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
        self.client = chromadb.PersistentClient(path="./chroma_db")
        self.collection = self.client.get_or_create_collection("news_articles")
    
    def chunk_text(self, text, chunk_size=200, overlap=50):
        words = text.split()
        chunks = []
        for i in range(0, len(words), chunk_size - overlap):
            chunk = ' '.join(words[i:i + chunk_size])
            if len(chunk.strip()) > 20:
                chunks.append(chunk)
        return chunks
    
    def add_articles(self, articles):
        for article in articles:
            chunks = self.chunk_text(article['content'])
            
            for i, chunk in enumerate(chunks):
                chunk_id = f"{article['url']}_{i}"
                embedding = self.model.encode(chunk).tolist()
                
                self.collection.add(
                    embeddings=[embedding],
                    documents=[chunk],
                    metadatas=[{
                        'title': article['title'],
                        'url': article['url'],
                        'source': article['source'],
                        'chunk_id': i
                    }],
                    ids=[chunk_id]
                )
    
    def search(self, query, top_k=5):
        query_embedding = self.model.encode(query).tolist()
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )
        return results