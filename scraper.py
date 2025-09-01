import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json

class NewsScraper:
    def __init__(self):
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    def scrape_article(self, url):
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract title
            title = soup.find('title')
            title = title.get_text().strip() if title else "No Title"
            
            # Extract paragraphs
            paragraphs = soup.find_all('p')
            content = ' '.join([p.get_text().strip() for p in paragraphs if p.get_text().strip()])
            
            return {
                'url': url,
                'title': title,
                'content': content,
                'scraped_at': datetime.now().isoformat(),
                'source': url.split('/')[2] if '/' in url else url
            }
        except Exception as e:
            print(f"Error scraping {url}: {e}")
            return None
    
    def scrape_multiple(self, urls):
        articles = []
        for url in urls:
            article = self.scrape_article(url)
            if article and len(article['content']) > 100:
                articles.append(article)
        return articles