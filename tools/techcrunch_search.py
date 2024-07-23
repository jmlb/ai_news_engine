"""
TechCrunch AI News Scraper

This script scrapes articles from the TechCrunch Artificial Intelligence category.
It retrieves article information including links, authors, snippets, and publication dates
for articles published within a specified time frame.

Usage:
    python techcrunch_ai_scraper.py

Dependencies:
    - requests
    - beautifulsoup4
    - python-dotenv

Author: Jean-Marc Beaujour (Improved by Assistant)
Date: July 21, 2024
Version: 2.0
License: MIT
"""

import re
import requests
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

@dataclass
class Article:
    title: str
    link: str
    author: Optional[str]
    snippet: str
    date: Optional[str]


class TechCrunchScraper:
    BASE_URL = "https://techcrunch.com/category/artificial-intelligence"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    def fetch_page(self) -> str:
        """Fetch the webpage content from TechCrunch."""
        response = self.session.get(self.BASE_URL)
        response.raise_for_status()
        return response.text


class ArticleParser:

    @staticmethod
    def parse_article(article_html: BeautifulSoup) -> Article:
        """Parse a single article HTML and return an Article object."""
        title_tag = article_html.find('h2', class_='wp-block-post-title')
        title = title_tag.find('a').text if title_tag else "Title not found"
        link = title_tag.find('a')['href'] if title_tag else None

        author_div = article_html.find('div', class_='wp-block-tc23-author-card-name')
        author = ArticleParser._extract_author(author_div) if author_div else None

        summary = article_html.find('p', class_='wp-block-post-excerpt__excerpt')
        snippet = summary.text.strip() if summary else "Summary not found"

        date = ArticleParser._extract_date(article_html)

        return Article(title, link, author, snippet, date)

    @staticmethod
    def _extract_author(author_div: BeautifulSoup) -> str:
        author_link = author_div.find('a')['href']
        author_match = re.search(r'/author/(.+?)/', author_link)
        return author_match.group(1).replace("-", " ") if author_match else "Unknown author"

    @staticmethod
    def _extract_date(article_html: BeautifulSoup) -> Optional[str]:
        time_tag = article_html.find('time', class_='wp-block-tc23-post-time-ago')
        if not time_tag:
            return None
        
        time_ago = time_tag.text.strip()
        days_ago = ArticleParser._convert_to_days_ago(time_ago)
        return ArticleParser._convert_to_date(days_ago)

    @staticmethod
    def _convert_to_days_ago(input_str: str) -> Optional[int]:
        if "hour" in input_str.lower():
            return 0
        elif "days ago" in input_str.lower():
            match = re.search(r'\d+', input_str)
            return int(match.group()) if match else None
        return None

    @staticmethod
    def _convert_to_date(days: Optional[int]) -> Optional[str]:
        if days is None:
            return None
        this_date = datetime.now().date() - timedelta(days=days)
        return this_date.strftime('%Y-%m-%d')


class TechCrunchNews:
    def __init__(self, days_back: int = 1):
        self.days_back = days_back
        self.scraper = TechCrunchScraper()
        self.parser = ArticleParser()

    def get_articles(self) -> List[Article]:
        """Fetch, parse, and filter articles from TechCrunch."""
        html_content = self.scraper.fetch_page()
        soup = BeautifulSoup(html_content, 'html.parser')
        articles_html = soup.find_all('div', class_='wp-block-tc23-post-picker')

        articles = [self.parser.parse_article(article_html) for article_html in articles_html]
        filtered_articles = self._filter_articles(articles)

        print(f"Found {len(filtered_articles)} articles published in the last {self.days_back} days")
        return filtered_articles

    def _filter_articles(self, articles: List[Article]) -> List[Article]:
        """Filter articles based on publication date."""
        cutoff_date = (datetime.now() - timedelta(days=self.days_back)).strftime('%Y-%m-%d')
        return [article for article in articles if article.date and article.date >= cutoff_date]


def main(days_back):
    techcrunch_engine = TechCrunchNews(days_back)
    articles = techcrunch_engine.get_articles()

    for article in articles:
        print(f"Title: {article.title}")
        print(f"Link: {article.link}")
        print(f"Author: {article.author}")
        print(f"Snippet: {article.snippet}")
        print(f"Date: {article.date}")
        print("---")

    return articles


if __name__ == "__main__":
    main(days_back=1)