from sentence_transformers import SentenceTransformer
import chromadb
import uuid

class EmbeddingManager:
    def __init__(self, model_name="all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
       
        self.client = chromadb.Client()
        self.collection = self.client.get_or_create_collection("news_articles")
    
    def chunk_text(self, text, chunk_size=200, overlap=50):
        words = text.split()
        chunks = []
        for i in range(0, len(words), chunk_size - overlap):
            chunk = ' '.join(words[i:i + chunk_size])
            if len(chunk.strip()) > 20:
                chunks.append(chunk)
        return chunks
    
    def clear_data(self):
        """Clear all stored data (reset cache)"""
        try:
            self.client.delete_collection("news_articles")
            self.collection = self.client.get_or_create_collection("news_articles")
        except Exception:
            pass  # Collection might not exist
    
    def add_articles(self, articles):
        for article in articles:
            chunks = self.chunk_text(article['content'])
            
            for chunk in chunks:
                embedding = self.model.encode(chunk).tolist()
                chunk_id = str(uuid.uuid4())
                
                self.collection.add(
                    embeddings=[embedding],
                    documents=[chunk],
                    metadatas=[{
                        'title': article['title'],
                        'url': article['url'],
                        'source': article['source']
                    }],
                    ids=[chunk_id]
                )

    
    def search(self, query, top_k=5):
        try:
            query_embedding = self.model.encode(query).tolist()
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k
            )
            return results
        except Exception:
            # Return empty results if collection is empty or error occurs
            return {'documents': [[]], 'metadatas': [[]]}