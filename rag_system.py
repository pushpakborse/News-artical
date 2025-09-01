import google.generativeai as genai
from embeddings import EmbeddingManager
from scraper import NewsScraper
import os
from dotenv import load_dotenv

class RAGSystem:
    def __init__(self):
        load_dotenv()
        self.embedding_manager = EmbeddingManager()
        self.scraper = NewsScraper()
        
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found. Please set it in .env file")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Hardcoded news URLs
        self.news_urls = [
            "https://timesofindia.indiatimes.com/",
            "https://www.hindustantimes.com/",
            "https://indianexpress.com/",
            "https://www.ndtv.com/",
            "https://www.thehindu.com/"
        ]
    
    def load_news(self):
        print("Loading news articles...")
        articles = self.scraper.scrape_multiple(self.news_urls)
        if articles:
            self.embedding_manager.add_articles(articles)
            print(f"✓ Loaded {len(articles)} articles from {len(self.news_urls)} sources")
            return True
        print("✗ No articles were successfully scraped")
        return False
    
    def query(self, question, top_k=3):
        # Retrieve relevant chunks
        results = self.embedding_manager.search(question, top_k)
        
        if not results['documents'][0]:
            return "No relevant information found in the database."
        
        # Prepare context from retrieved chunks
        context_chunks = results['documents'][0]
        sources = [meta['url'] for meta in results['metadatas'][0]]
        
        context = "\n\n".join(context_chunks)
        
        # Generate answer using Gemini
        prompt = f"""You are a helpful news assistant. Based on the following news context, provide a well-structured and clear answer.

Context:
{context}

Question: {question}

Provide a clear, organized answer with proper formatting. Use bullet points or numbered lists when appropriate."""
        
        try:
            response = self.model.generate_content(prompt)
            answer = response.text.strip()
        except Exception as e:
            answer = f"Error generating response: {e}"
        
        return {
            'answer': answer,
            'sources': list(set(sources)),
            'context_used': len(context_chunks),
            'retrieved_chunks': context_chunks
        }