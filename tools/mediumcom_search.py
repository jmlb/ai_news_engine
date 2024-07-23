"""
Medium Article Scraper

This script scrapes and processes Medium articles based on given topics and subtopics.
It uses Selenium WebDriver to navigate Medium pages and BeautifulSoup for HTML parsing.

Author: Jean-Marc Beaujour (Improved by Assistant)
Date: 2024-07-21
Version: 2.2

Dependencies:
- Python 3.7+
- selenium
- beautifulsoup4
- langdetect

Usage:
1. Ensure all dependencies are installed:
   pip install selenium beautifulsoup4 langdetect

2. Download and install the appropriate ChromeDriver for your system:
   https://sites.google.com/a/chromium.org/chromedriver/downloads

3. Run the script:
   python medium_ai_fetcher.py

Note: Adjust the 'interests' and 'related_tags' lists in the __main__ section
      to customize the topics and subtopics for scraping.

This script is for educational purposes only. Ensure you comply with Medium's
terms of service and robots.txt file when using this script.
"""

import re
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Set
from dataclasses import dataclass
from langdetect import detect
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

@dataclass
class MediumArticle:
    title: str
    link: str
    img: Optional[str]
    snippet: str
    date: Optional[str]
    topic: str


class WebDriverManager:
    def __init__(self):
        self.driver = self.initialize_driver()

    @staticmethod
    def initialize_driver() -> webdriver.Chrome:
        options = webdriver.ChromeOptions()
        options.add_argument('--disable-gpu')
        return webdriver.Chrome(options=options)

    def quit(self):
        self.driver.quit()

class MediumScraper:
    def __init__(self, driver: webdriver.Chrome):
        self.driver = driver

    def fetch_page(self, url: str):
        self.driver.get(url)
        try:
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'article')))
        except TimeoutException:
            print(f"Timeout waiting for page load: {url}")

    def scroll_page(self):
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)  # Wait for new content to load

    def get_page_source(self) -> str:
        return self.driver.page_source


class ArticleParser:
    @staticmethod
    def parse_article(article: BeautifulSoup, topic: str) -> Optional[MediumArticle]:
        title = ArticleParser.extract_title(article)
        link = ArticleParser.extract_links(article)
        img = ArticleParser.extract_image(article)
        snippet = ArticleParser.extract_snippet(article)
        date = ArticleParser.extract_post_date(article)

        if title and link and snippet:
            return MediumArticle(title, link, img, snippet, date, topic)
        return None

    @staticmethod
    def extract_title(article: BeautifulSoup) -> Optional[str]:
        h2s = [h2.get_text(strip=True) for h2 in article.find_all('h2')]
        h2_texts = [x for x in h2s if len(x) > 0]
        
        aria_labels = [x.get("aria-label") for x in article.find_all('div')]
        titles = [x for x in aria_labels if isinstance(x, str) and len(x) > 0]
        titles += h2_texts

        title = titles[0] if titles else None
        return ArticleParser.convert_unicode_escapes(title)

    @staticmethod
    def extract_links(article: BeautifulSoup) -> Optional[str]:
        data_href = [a.get('data-href') for a in article.find_all('div') if a.get('data-href')]
        links = [x for x in data_href if len(x) > 0 and "https" in x]
        return links[0] if links else None

    @staticmethod
    def extract_image(article: BeautifulSoup) -> Optional[str]:
        srcs = list(set([x.get("src") for x in article.find_all('img')]))
        imgs = [img for img in srcs if ".jpg" in img.lower() or ".png" in img.lower() or ".jpeg" in img.lower()]
        return imgs[0] if imgs else None

    @staticmethod
    def extract_snippet(article: BeautifulSoup) -> Optional[str]:
        h3s = [h3.get_text(strip=True) for h3 in article.find_all('h3')]
        h3_texts = [x for x in h3s if len(x) > 0]
        snippet = h3_texts[0] if h3_texts else None
        return ArticleParser.convert_unicode_escapes(snippet)

    @staticmethod
    def extract_post_date(article: BeautifulSoup) -> Optional[str]:
        divs = article.find_all("div")
        div_texts = [ArticleParser.convert_to_days_ago(x.get_text(strip=True)) for x in divs if x.get_text(strip=True)]
        ages = [ArticleParser.convert_to_days_ago(age) for div_text in div_texts for age in ArticleParser.extract_post_age(div_text) if age]
        age = ages[0] if ages else None
        if age:
            match = re.search(r'(\d+)d ago', age)
            if match:
                age_in_days = int(match.group(1))
                return ArticleParser.convert_to_date(age_in_days)
        return None

    @staticmethod
    def extract_post_age(input_str: str) -> List[str]:
        pattern = r'\b\d{1,2}[hd] ago'
        matches = re.findall(pattern, input_str)
        return [ArticleParser.convert_to_days_ago(x) for x in matches]

    @staticmethod
    def convert_to_days_ago(input_str: str) -> str:
        if input_str.lower() == "just now":
            return "0d ago"
        elif "h ago" in input_str.lower():
            return "0d ago"
        else:
            return input_str.lower()

    @staticmethod
    def convert_to_date(days: int) -> str:
        target_date = datetime.now() - timedelta(days=days)
        return target_date.strftime('%Y-%m-%d')

    @staticmethod
    def convert_unicode_escapes(text: Optional[str]):
        if not isinstance(text, str):
            return text
        
        def replace_unicode(match):
            return chr(int(match.group(1), 16))
        
        pattern = r'\\u([0-9a-fA-F]{4})'
        return re.sub(pattern, replace_unicode, text)


class MediumNewsFetcher:
    def __init__(self, topics: List[str], subtopics: List[str], days_back: int):
        self.topics = topics
        self.subtopics = subtopics
        self.days_back = days_back
        self.driver_manager = WebDriverManager()
        self.scraper = MediumScraper(self.driver_manager.driver)
        self.parser = ArticleParser()

    def fetch_articles(self) -> List[MediumArticle]:
        all_articles = []
        for topic in self.topics:
            url = f"https://medium.com/tag/{topic}/archive"
            self.scraper.fetch_page(url)
            
            seen_links: Set[str] = set()
            consecutive_no_new = 0
            max_consecutive_no_new = 3  # Stop after 3 consecutive scrolls with no new articles

            while consecutive_no_new < max_consecutive_no_new:
                new_articles = self.process_current_page(topic, seen_links)
                
                if new_articles:
                    all_articles.extend(new_articles)
                    consecutive_no_new = 0
                else:
                    consecutive_no_new += 1
                
                self.scraper.scroll_page()

            print(f"Finished scraping for topic: {topic}. Articles found: {len(all_articles)}")

        self.driver_manager.quit()
        return self.remove_duplicate_articles(all_articles)

    def process_current_page(self, topic: str, seen_links: Set[str]) -> List[MediumArticle]:
        html_content = self.scraper.get_page_source()
        soup = BeautifulSoup(html_content, 'html.parser')
        articles = soup.find_all('article')
        
        new_articles = []
        for article in articles:
            parsed_article = self.parser.parse_article(article, topic)
            if parsed_article and self.is_valid_article(parsed_article) and parsed_article.link not in seen_links:
                new_articles.append(parsed_article)
                seen_links.add(parsed_article.link)
        
        return new_articles

    def is_valid_article(self, article: MediumArticle) -> bool:
        if not article.date:
            return False
        article_date = datetime.strptime(article.date, "%Y-%m-%d").date()
        cutoff_date = (datetime.now() - timedelta(days=self.days_back)).date()
        return article_date >= cutoff_date and detect(article.title) == "en"

    @staticmethod
    def remove_duplicate_articles(articles: List[MediumArticle]) -> List[MediumArticle]:
        unique_articles = []
        seen_links = set()
        for article in articles:
            if article.link and article.link not in seen_links:
                unique_articles.append(article)
                seen_links.add(article.link)
        return unique_articles


def main(interests = ["llm", "large-language-models"],
         related_tags = ["data-science", "prompt-engineering", "mathematical-reasoning", 
                    "nlp", "time-series", "text-generation", "artificial-intelligence", "ai"],
         max_age = 1):

    fetcher = MediumNewsFetcher(interests, related_tags, max_age)
    articles = fetcher.fetch_articles()

    print(f"Total unique articles found: {len(articles)}")
    for article in articles:
        print(f"Title: {article.title}")
        print(f"Link: {article.link}")
        print(f"Topic: {article.topic}")
        print(f"Date: {article.date}")
        print(f"Snippet: {article.snippet}")
        print(f"Image URL: {article.img}")
        print("---")
    
    return articles


if __name__ == "__main__":
    main()
