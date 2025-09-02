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
        
        # Available news sources
        self.available_sources = {
            '1': {'name': 'Times of India', 'url': 'https://timesofindia.indiatimes.com/'},
            '2': {'name': 'Hindustan Times', 'url': 'https://www.hindustantimes.com/'},
            '3': {'name': 'Indian Express', 'url': 'https://indianexpress.com/'},
            '4': {'name': 'NDTV', 'url': 'https://www.ndtv.com/'},
            '5': {'name': 'The Hindu', 'url': 'https://www.thehindu.com/'},
            '6': {'name': 'CNN', 'url': 'https://www.cnn.com/'},
            '7': {'name': 'BBC News', 'url': 'https://www.bbc.com/news'},
            '8': {'name': 'Reuters', 'url': 'https://www.reuters.com/'}
        }
        self.selected_sources = []
    
    def select_sources(self):
        print("\nAvailable News Sources:")
        print("=" * 40)
        for key, source in self.available_sources.items():
            print(f"{key}. {source['name']}")
        
        print("\nSelect sources (comma-separated numbers, e.g., 1,3,5):")
        print("Or press Enter for all sources")
        
        choice = input("Your choice: ").strip()
        
        if not choice:
            self.selected_sources = list(self.available_sources.values())
        else:
            selected_keys = [k.strip() for k in choice.split(',')]
            self.selected_sources = [self.available_sources[k] for k in selected_keys if k in self.available_sources]
        
        print(f"\nSelected {len(self.selected_sources)} sources:")
        for source in self.selected_sources:
            print(f"• {source['name']}")
    
    def load_news(self):
        if not self.selected_sources:
            print("No sources selected!")
            return False
            
        print("\nLoading news articles...")
        urls = [source['url'] for source in self.selected_sources]
        articles = self.scraper.scrape_multiple(urls)
        
        if articles:
            self.embedding_manager.add_articles(articles)
            print(f"✓ Loaded {len(articles)} articles from {len(self.selected_sources)} sources")
            return True
        print("✗ No articles were successfully scraped")
        return False
    
    def query(self, question, top_k=3):
        # Retrieve relevant chunks with better filtering
        results = self.embedding_manager.search(question, top_k, similarity_threshold=0.4)
        
        if not results['documents'][0]:
            return "No relevant information found in the database."
        
        # Prepare context from retrieved chunks
        context_chunks = results['documents'][0]
        sources = [meta['url'] for meta in results['metadatas'][0]]
        
        context = "\n\n".join(context_chunks)
        
        # Create citations mapping with unique URLs (one per article)
        citations = {}
        seen_urls = set()
        citation_num = 1
        
        for meta in results['metadatas'][0]:
            url = meta['url']
            if url not in seen_urls:
                seen_urls.add(url)
                citations[str(citation_num)] = url
                citation_num += 1
        
        # Generate answer with inline citations using Gemini
        prompt = f"""You are a helpful news assistant. Answer the question based ONLY on the provided context.

Context:
{context}

Question: {question}

Instructions:
1. Answer the question using the provided context
2. Add citations [1], [2], [3] etc. after sentences that reference specific information
3. Use different citation numbers for different sources
4. Maximum {len(citations)} citations available
5. Be specific and relevant to the question"""
        
        try:
            response = self.model.generate_content(prompt)
            answer = response.text.strip()
        except Exception as e:
            answer = f"Error generating response: {e}"
        
        # Store citations for later access
        self.last_citations = citations
        
        return {
            'answer': answer,
            'sources': list(set(sources)),
            'context_used': len(context_chunks),
            'citations': citations
        }