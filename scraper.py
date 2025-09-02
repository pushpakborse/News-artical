import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json

class NewsScraper:
    def __init__(self):
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    def get_article_links(self, base_url):
        """Extract article links from news website homepage"""
        try:
            response = requests.get(base_url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            links = set()
            domain = base_url.split('/')[2]
            
            # Get all links
            for link in soup.find_all('a', href=True):
                href = link['href']
                
                # Convert relative URLs to absolute
                if href.startswith('/'):
                    href = f"https://{domain}{href}"
                elif href.startswith('../'):
                    href = f"https://{domain}/{href[3:]}"
                elif not href.startswith('http'):
                    href = f"https://{domain}/{href}"
                
                # Filter for news articles with better patterns
                if (domain in href and 
                    len(href.split('/')) > 4 and  # Has path segments
                    not any(skip in href.lower() for skip in ['video', 'photo', 'gallery', 'live', 'javascript:', 'mailto:', '#'])):
                    
                    # Check if it looks like an article URL
                    if (any(pattern in href.lower() for pattern in ['/news/', '/article/', '/story/', '/politics/', '/sports/', '/business/', '/india/', '/world/']) or
                        any(char.isdigit() for char in href.split('/')[-1])):
                        links.add(href)
            
            print(f"Found {len(links)} article links from {domain}")
            return list(links)[:8]  # Get more articles
        except Exception as e:
            print(f"Error getting links from {base_url}: {e}")
            return []
    
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
    
    def scrape_multiple(self, base_urls):
        articles = []
        for base_url in base_urls:
            print(f"Getting articles from {base_url}...")
            article_links = self.get_article_links(base_url)
            
            for article_url in article_links:
                print(f"Scraping: {article_url[:60]}...")
                article = self.scrape_article(article_url)
                if article and len(article['content']) > 200:
                    articles.append(article)
                    print(f"✓ Added: {article['title'][:50]}...")
                    
        print(f"Total articles scraped: {len(articles)}")
        return articles