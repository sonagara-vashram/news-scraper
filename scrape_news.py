import sys
import logging
from typing import Optional, Dict, Any
from urllib.parse import urlparse
from fake_useragent import UserAgent
import requests
from bs4 import BeautifulSoup
from requests.exceptions import RequestException, Timeout, ConnectionError


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class NewsScraperError(Exception):
    """Custom exception for news scraper errors."""
    pass

class NewsScraper:
    """
    A professional news article scraper with validations.
    """
    
    def __init__(self, timeout: int = 30, headers: Optional[Dict[str, str]] = None):
        self.timeout = timeout
        self.user_agent = UserAgent()
        self.headers = headers or {
            'User-Agent': self.user_agent.random
        }
    
    def validate_url(self, url: str) -> bool:
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception as e:
            logger.error(f"URL validation error: {e}")
            return False
    
    def fetch_page_content(self, url: str) -> requests.Response:
        """
        Fetch the content of a web page.
        
        Args:
            url (str): URL of the page to fetch
            
        Returns:
            requests.Response: Response object containing page content
            
        Raises:
            NewsScraperError: If the page cannot be fetched
        """
        if not self.validate_url(url):
            raise NewsScraperError(f"Invalid URL format: {url}")
        
        try:
            logger.info(f"Fetching content from: {url}")
            response = requests.get(
                url,
                headers=self.headers,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response
            
        except Timeout:
            raise NewsScraperError(f"Request timeout after {self.timeout} seconds")
        except ConnectionError:
            raise NewsScraperError(f"Connection error while accessing {url}")
        except RequestException as e:
            raise NewsScraperError(f"Request failed: {str(e)}")
    
    def extract_title(self, soup: BeautifulSoup) -> str:
        """
        Extract the title from the parsed HTML.
        
        Args:
            soup (BeautifulSoup): Parsed HTML content
            
        Returns:
            str: Extracted title or default message
        """
        # Try multiple selectors for title extraction
        title_selectors = [
            'h1',
            'title',
            '[data-testid="headline"]',
            '.headline',
            '.article-title'
        ]
        
        for selector in title_selectors:
            title_element = soup.select_one(selector)
            if title_element:
                title = title_element.get_text(strip=True)
                if title:
                    logger.info(f"Title extracted using selector: {selector}")
                    return title
        
        logger.warning("No title found using any selector")
        return "No title found"
    
    def extract_content(self, soup: BeautifulSoup) -> str:
        """
        Extract the main content from the parsed HTML.
        
        Args:
            soup (BeautifulSoup): Parsed HTML content
            
        Returns:
            str: Extracted content
        """
        # Try multiple selectors for content extraction
        content_selectors = [
            'div.zn-body__paragraph',
            'div[data-testid="article-text"]',
            'div.article-content p',
            'article p',
            'main p',
            '.content p',
            'p'
        ]
        
        content_paragraphs = []
        
        for selector in content_selectors:
            paragraphs = soup.select(selector)
            if paragraphs:
                content_paragraphs = [
                    p.get_text(strip=True) 
                    for p in paragraphs 
                    if p.get_text(strip=True)
                ]
                if content_paragraphs:
                    logger.info(f"Content extracted using selector: {selector}")
                    break
        
        if not content_paragraphs:
            logger.warning("No content paragraphs found")
            return "No content available"
        
        return " ".join(content_paragraphs)
    
    def extract_author(self, soup: BeautifulSoup) -> str:
        """
        Extract the author name from the parsed HTML.
        
        Args:
            soup (BeautifulSoup): Parsed HTML content
            
        Returns:
            str: Extracted author name or default message
        """
        # Try multiple selectors and attributes for author extraction
        author_selectors = [
            # Common class-based selectors
            '.author',
            '.author-name',
            '.byline',
            '.byline-author',
            '.article-author',
            '.writer',
            '.journalist',
            '.reporter',
            '.by-author',
            '.post-author',
            '.story-author',
            # Data attribute selectors
            '[data-testid="author"]',
            '[data-testid="byline"]',
            '[data-author]',
            # Itemprop selectors (structured data)
            '[itemprop="author"]',
            '[itemprop="name"]',
            # Rel attribute selectors
            '[rel="author"]',
            # Common tag combinations
            'span.author',
            'div.author',
            'p.author',
            'a.author',
            'span.byline',
            'div.byline',
            # Meta tags
            'meta[name="author"]',
            'meta[property="article:author"]'
        ]
        
        # First, try direct selectors
        for selector in author_selectors:
            try:
                elements = soup.select(selector)
                for element in elements:
                    # For meta tags, get content attribute
                    if element.name == 'meta':
                        author_text = element.get('content', '').strip()
                    else:
                        author_text = element.get_text(strip=True)
                    
                    # Validate author text
                    if author_text and len(author_text) > 0:
                        # Clean up common prefixes
                        author_text = self._clean_author_text(author_text)
                        if author_text:
                            logger.info(f"Author extracted using selector: {selector}")
                            return author_text
            except Exception as e:
                logger.debug(f"Error with selector {selector}: {e}")
                continue
        
        # Try to find elements containing "author" in their class or attributes
        all_elements = soup.find_all(attrs={"class": True})
        for element in all_elements:
            classes = ' '.join(element.get('class', []))
            if 'author' in classes.lower():
                author_text = element.get_text(strip=True)
                if author_text:
                    author_text = self._clean_author_text(author_text)
                    if author_text:
                        logger.info(f"Author found in element with classes: {classes}")
                        return author_text
        
        # Try to find elements with attributes containing "author"
        for element in soup.find_all():
            for attr_name, attr_value in element.attrs.items():
                if isinstance(attr_value, str) and 'author' in attr_value.lower():
                    author_text = element.get_text(strip=True)
                    if author_text:
                        author_text = self._clean_author_text(author_text)
                        if author_text:
                            logger.info(f"Author found in element with attribute {attr_name}={attr_value}")
                            return author_text
        
        # Last resort: look for common patterns in text
        text_patterns = [
            'By ',
            'Written by ',
            'Author: ',
            'Reporter: ',
            'Journalist: '
        ]
        
        for pattern in text_patterns:
            elements = soup.find_all(string=lambda text: text and pattern in text)
            for element in elements:
                text = element.strip()
                if pattern in text:
                    # Extract text after the pattern
                    author_text = text.split(pattern, 1)[1].split('\n')[0].split('|')[0].strip()
                    if author_text:
                        logger.info(f"Author found using pattern: {pattern}")
                        return author_text
        
        logger.warning("No author found using any method")
        return "Author not found"
    
    def _clean_author_text(self, author_text: str) -> str:
        """
        Clean and validate author text.
        
        Args:
            author_text (str): Raw author text
            
        Returns:
            str: Cleaned author text or empty string if invalid
        """
        if not author_text:
            return ""
        
        # Remove common prefixes and suffixes
        prefixes_to_remove = [
            'By ', 'by ', 'BY ',
            'Author: ', 'author: ', 'AUTHOR: ',
            'Written by ', 'written by ',
            'Reporter: ', 'reporter: ',
            'Journalist: ', 'journalist: '
        ]
        
        cleaned = author_text
        for prefix in prefixes_to_remove:
            if cleaned.startswith(prefix):
                cleaned = cleaned[len(prefix):].strip()
        
        # Remove common suffixes
        suffixes_to_remove = [
            ' |', ' -', ' •'
        ]
        
        for suffix in suffixes_to_remove:
            if cleaned.endswith(suffix):
                cleaned = cleaned[:-len(suffix)].strip()
        
        # Basic validation - should be reasonable length and contain letters
        if len(cleaned) < 2 or len(cleaned) > 100:
            return ""
        
        # Should contain at least some letters
        if not any(c.isalpha() for c in cleaned):
            return ""
        
        # Remove extra whitespace
        cleaned = ' '.join(cleaned.split())
        
        return cleaned
    
    def scrape_article(self, url: str) -> Dict[str, Any]:
        """
        Scrape a news article from the given URL.
        
        Args:
            url (str): URL of the article to scrape
            
        Returns:
            dict: Dictionary containing title, content, and metadata
            
        Raises:
            NewsScraperError: If scraping fails
        """
        try:
            # Fetch page content
            response = self.fetch_page_content(url)
            
            # Parse HTML content
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Extract title, content, and author
            title = self.extract_title(soup)
            content = self.extract_content(soup)
            author = self.extract_author(soup)
            
            # Prepare result
            result = {
                'url': url,
                'title': title,
                'content': content,
                'author': author,
                'content_length': len(content),
                'status_code': response.status_code,
                'success': True
            }
            
            logger.info(f"Successfully scraped article: {title[:50]}...")
            return result
            
        except NewsScraperError:
            raise
        except Exception as e:
            raise NewsScraperError(f"Unexpected error during scraping: {str(e)}")
    
    def display_article(self, article_data: Dict[str, Any]) -> None:
        """
        Display the scraped article in a formatted manner.
        
        Args:
            article_data (dict): Article data dictionary
        """
        print("\n" + "=" * 80)
        print("NEWS ARTICLE SCRAPER")
        print("=" * 80)
        print(f"URL: {article_data['url']}")
        print(f"Status: {'SUCCESS' if article_data['success'] else 'FAILED'}")
        print(f"Content Length: {article_data['content_length']} characters")
        print("-" * 80)
        print(f"TITLE: {article_data['title']}")
        print(f"AUTHOR: {article_data['author']}")
        print("-" * 80)
        print("CONTENT:")
        print(article_data['content'])
        print("=" * 80)


def main():
    """
    Main function to handle command line execution.
    """
    if len(sys.argv) < 2:
        print("Usage: python scrape_news.py <article_url>")
        print("Example: python scrape_news.py https://example.com/news-article")
        sys.exit(1)
    
    url = sys.argv[1]
    scraper = NewsScraper()
    
    try:
        article_data = scraper.scrape_article(url)
        scraper.display_article(article_data)
        
    except NewsScraperError as e:
        logger.error(f"Scraping failed: {e}")
        print(f"Error: {e}")
        sys.exit(1)
        
    except KeyboardInterrupt:
        logger.info("Scraping interrupted by user")
        print("\nScraping interrupted by user")
        sys.exit(0)
        
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()