# 📰 Professional News Scraper

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Code Style](https://img.shields.io/badge/code%20style-professional-brightgreen.svg)](https://github.com/sonagara-vashram/news-scraper)

A robust, enterprise-grade Python news article scraper that intelligently extracts **titles**, **content**, and **author information** from web pages with advanced error handling, multiple extraction strategies, and professional logging.

## ✨ Key Features

### 🎯 **Smart Content Extraction**
- **Title Extraction**: Multiple CSS selectors and fallback strategies
- **Content Extraction**: Intelligent paragraph detection across different news sites
- **Author Detection**: Advanced author name extraction using 30+ selection methods
- **Metadata Extraction**: URL validation, content length, and status tracking

### 🛡️ **Enterprise-Grade Reliability**
- **Robust Error Handling**: Custom exceptions with detailed error messages
- **Network Resilience**: Timeout handling, connection error recovery
- **URL Validation**: Comprehensive URL format validation
- **Request Optimization**: Random User-Agent rotation to avoid blocking

### 🔧 **Professional Architecture**
- **Object-Oriented Design**: Clean, maintainable code structure
- **Type Annotations**: Full type hints for better IDE support
- **Comprehensive Logging**: Detailed logging for debugging and monitoring
- **Configurable Settings**: Customizable timeouts and headers

### 🎨 **User Experience**
- **Beautiful Output**: Professional formatting with clear sections
- **Progress Tracking**: Real-time logging of extraction progress
- **Error Reporting**: Clear, actionable error messages
- **Command Line Interface**: Simple, intuitive CLI

## 🚀 Quick Start

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/sonagara-vashram/news-scraper.git
cd news-scraper
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

### Basic Usage

```bash
python scrape_news.py https://example.com/news-article
```

**Example Output:**
```
================================================================================
NEWS ARTICLE SCRAPER
================================================================================
URL: https://example.com/news-article
Status: SUCCESS
Content Length: 1245 characters
--------------------------------------------------------------------------------
TITLE: Breaking: Major News Story Unfolds
AUTHOR: John Smith, Senior Reporter
--------------------------------------------------------------------------------
CONTENT:
This is the extracted article content with all paragraphs properly joined...
================================================================================
```

## 📚 Advanced Usage

### Programmatic Integration

```python
from scrape_news import NewsScraper

# Initialize with custom settings
scraper = NewsScraper(
    timeout=30,  # 30-second timeout
    headers={
        'User-Agent': 'Custom News Bot 1.0',
        'Accept': 'text/html,application/xhtml+xml'
    }
)

# Scrape an article
try:
    article_data = scraper.scrape_article("https://news-site.com/article")
    
    # Access extracted data
    print(f"Title: {article_data['title']}")
    print(f"Author: {article_data['author']}")
    print(f"Content Length: {article_data['content_length']} chars")
    print(f"Content: {article_data['content'][:200]}...")
    
except NewsScraperError as e:
    print(f"Scraping failed: {e}")
```

### Batch Processing

```python
urls = [
    "https://site1.com/article1",
    "https://site2.com/article2",
    "https://site3.com/article3"
]

scraper = NewsScraper()
results = []

for url in urls:
    try:
        article = scraper.scrape_article(url)
        results.append(article)
        print(f"Successfully scraped: {article['title'][:50]}...")
    except NewsScraperError as e:
        print(f"Failed to scrape {url}: {e}")

print(f"\nSuccessfully scraped {len(results)} articles")
```

## 🏗️ Architecture Overview

### Core Classes

| Class | Description |
|-------|-------------|
| `NewsScraper` | Main scraper class with all extraction methods |
| `NewsScraperError` | Custom exception for scraper-specific errors |

### Key Methods

| Method | Purpose | Returns |
|--------|---------|---------|
| `validate_url()` | Validates URL format and structure | `bool` |
| `fetch_page_content()` | Downloads webpage with error handling | `requests.Response` |
| `extract_title()` | Extracts article title using multiple strategies | `str` |
| `extract_content()` | Extracts main article content | `str` |
| `extract_author()` | Extracts author name using 30+ methods | `str` |
| `scrape_article()` | Orchestrates the complete scraping process | `Dict[str, Any]` |
| `display_article()` | Formats and displays scraped content | `None` |

## 🎯 Author Extraction Intelligence

Our advanced author detection system uses multiple strategies:

### 🔍 **CSS Selectors** (Primary)
- `.author`, `.author-name`, `.byline`, `.writer`
- `[data-testid="author"]`, `[itemprop="author"]`
- `meta[name="author"]`, `meta[property="article:author"]`

### 🧠 **Smart Pattern Recognition**
- Text patterns: "By ", "Written by ", "Author: "
- Class name analysis containing "author"
- Attribute value scanning for author-related terms

### 🧹 **Text Cleaning & Validation**
- Removes common prefixes (By, Author:, etc.)
- Validates reasonable length (2-100 characters)
- Ensures alphabetic content presence
- Handles multiple name formats

## ⚙️ Configuration Options

```python
# Default configuration
scraper = NewsScraper()

# Custom timeout (default: 30 seconds)
scraper = NewsScraper(timeout=60)

# Custom headers
scraper = NewsScraper(
    timeout=45,
    headers={
        'User-Agent': 'NewsBot/1.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive'
    }
)
```

## 🛠️ Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `beautifulsoup4` | 4.13.5+ | HTML parsing and CSS selection |
| `requests` | 2.32.5+ | HTTP requests and response handling |
| `fake-useragent` | 2.2.0+ | Random User-Agent generation |

## 📊 Supported News Sites

The scraper is designed to work with various news websites including:

- 📺 **CNN** - `.zn-body__paragraph` selector optimization
- 📰 **General News Sites** - Multiple fallback selectors
- 🌐 **Blog Platforms** - Article and main tag support
- 📱 **Mobile Sites** - Responsive design compatibility

## 🐛 Error Handling

### Exception Hierarchy
```
NewsScraperError
├── Invalid URL Format
├── Request Timeout
├── Connection Error
└── HTTP Status Errors
```

### Common Scenarios
```python
try:
    article = scraper.scrape_article(url)
except NewsScraperError as e:
    if "timeout" in str(e).lower():
        print("⏰ Request timed out - try increasing timeout")
    elif "connection" in str(e).lower():
        print("🌐 Network connection issue")
    elif "invalid url" in str(e).lower():
        print("🔗 URL format is incorrect")
    else:
        print(f"❌ Scraping error: {e}")
```

## 📝 Logging

The scraper provides comprehensive logging:

```python
import logging

# Enable debug logging
logging.getLogger('scrape_news').setLevel(logging.DEBUG)

# Log levels used:
# INFO: Successful extractions, progress updates
# WARNING: Fallback methods used, missing elements
# ERROR: Request failures, parsing errors
# DEBUG: Detailed selector attempts
```

## 🤝 Contributing

We welcome contributions! Here's how to get started:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Development Guidelines

- Follow PEP 8 style guidelines
- Add type hints for all functions
- Include docstrings for public methods
- Add tests for new features
- Update documentation as needed

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🌟 Support

If you find this project helpful, please consider:

- ⭐ **Starring** the repository
- 🐛 **Reporting** bugs or requesting features via Issues
- 🔄 **Sharing** with others who might benefit

## 📞 Contact

- **GitHub**: [@sonagara-vashram](https://github.com/sonagara-vashram)
- **Repository**: [news-scraper](https://github.com/sonagara-vashram/news-scraper)

---

<div align="center">

**Built with ❤️ for the developer community**

</div>