from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

class EmbeddingManager:
    def __init__(self, model_name="all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
        self.embeddings = []
        self.documents = []
        self.metadatas = []
    
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
            
            for chunk in chunks:
                embedding = self.model.encode(chunk)
                
                self.embeddings.append(embedding)
                self.documents.append(chunk)
                self.metadatas.append({
                    'title': article['title'],
                    'url': article['url'],
                    'source': article['source']
                })

    
    def search(self, query, top_k=5, similarity_threshold=0.3):
        if not self.embeddings:
            return {'documents': [[]], 'metadatas': [[]]}
        
        query_embedding = self.model.encode(query).reshape(1, -1)
        embeddings_matrix = np.array(self.embeddings)
        
        similarities = cosine_similarity(query_embedding, embeddings_matrix)[0]
        
        # Filter by similarity threshold for better relevance
        relevant_indices = [i for i, sim in enumerate(similarities) if sim >= similarity_threshold]
        
        if not relevant_indices:
            # If no results above threshold, take top results anyway
            relevant_indices = np.argsort(similarities)[::-1][:top_k]
        else:
            # Sort by similarity and take top_k
            relevant_indices = sorted(relevant_indices, key=lambda i: similarities[i], reverse=True)[:top_k]
        
        results = {
            'documents': [[self.documents[i] for i in relevant_indices]],
            'metadatas': [[self.metadatas[i] for i in relevant_indices]]
        }
        return results