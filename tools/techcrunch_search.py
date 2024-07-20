import pytz
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta



class TechCrunchNews:
    def __init__(self, topics):
        """
        Initialize the TechCrunchNews object with the URL for TechCrunch main page and a list of topics to filter.
        
        Args:
            topics (list): List of topics to filter articles
        """
        self.url = "https://techcrunch.com/"
        # List of topics to filter
        self.topics = topics

    def fetch_page(self,):
        """
        Fetch the webpage content from TechCrunch.

        Returns:
            HTML content of the TechCrunch main page
        """
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(self.url, headers=headers)
        response.raise_for_status()  # Raise an exception for bad status codes
        return response.text

    @staticmethod
    def parse_articles(html_content):
        """
        Parse the HTML content and extract article information.

        Args:
            html_content: HTML content of the TechCrunch main page
        Returns:
            List of dictionaries containing article information
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        articles = soup.find_all('div', class_='post-block')
        
        parsed_articles = []
        for article in articles:
            title_element = article.find('h2', class_='post-block__title')
            if title_element:
                title = title_element.text.strip()
                link = title_element.a['href']
                
                excerpt_element = article.find('div', class_='post-block__content')
                excerpt = excerpt_element.text.strip() if excerpt_element else "No excerpt available"
                
                author_element = article.find('span', class_='river-byline__authors')
                author = author_element.text.strip() if author_element else "Unknown Author"
                
                date_element = article.find('time', class_='river-byline__time')
                if date_element:
                    date_str = date_element['datetime']
                    date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                else:
                    date = None
                
                parsed_articles.append({
                    'title': title,
                    'link': link,
                    'excerpt': excerpt,
                    'author': author,
                    'date': date
                })
        
        return parsed_articles

    @staticmethod
    def is_today(article_date):
        """
        Check if the article is from today.

        Args:
            article_date: The date of the article
        Returns:
            True if the article is from today, otherwise False
        """
        print(article_date)
        if article_date is None:
            return False
        today = datetime.now(pytz.utc).date()
        return article_date.date() == today

    def is_relevant_topic(self, article):
        """
        Check if the article is about any of the specified topics.

        Args:
            article: Dictionary containing article information
        Returns:
            True if the article is relevant to the specified topics, otherwise False
        """
        content = (article['title'] + ' ' + article['excerpt']).lower()
        return any(topic.lower() in content for topic in self.topics)


    def __call__(self,):
        """
        Fetch, parse, and filter articles from TechCrunch based on the specified topics and if they are from today.

        Returns:
            List of relevant articles published today
        """
        relevant_articles = []
        try:
            html_content = self.fetch_page()
            articles = self.parse_articles(html_content)

            relevant_articles = [
                article for article in articles 
                if self.is_today(article['date']) and self.is_relevant_topic(article)
            ]
            
            print(f"Found {len(relevant_articles)} articles published today on TechCrunch about {', '.join(self.topics)}:")
            
        except requests.RequestException as e:
            print(f"An error occurred while fetching the webpage: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

        return relevant_articles


if __name__ == "__main__":
    topics = ["large language models", "AI", "artificial intelligence", "machine learning"]
    techcrunch_engine = TechCrunchNews(topics)
    
    posts = techcrunch_engine()
