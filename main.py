"""
AI News Aggregator with SQLite Storage

This script aggregates AI-related news from multiple sources including Reddit, YouTube, TechCrunch, and Medium.
It uses custom scrapers for each platform to fetch recent, relevant content and stores the results in a SQLite database.

Usage:
    python main.py

Dependencies:
    - praw
    - google-api-python-client
    - selenium
    - beautifulsoup4
    - langdetect
    - requests
    - python-dotenv
    - pandas
    - sqlite3

Author: Jean-Marc Beaujour (Improved by Assistant)
Date: 2024-07-21
Version: 2.1
License: MIT
"""

import os
import sqlite3
from typing import List, Dict, Any
from dotenv import load_dotenv
from datetime import datetime
import pandas as pd

# Import our custom scraper classes
from tools.reddit_search import RedditNewsFetcher, RedditPost
from tools.youtube_search import YouTubeNewsFetcher, Video
from tools.techcrunch_search import TechCrunchNews, Article as TechCrunchArticle
from tools.mediumcom_search import MediumNewsFetcher, MediumArticle


# Load environment variables
load_dotenv()


# Configuration
CONFIGS = {
    "REDDIT_CLIENT_ID": os.getenv("REDDIT_CLIENT_ID"),
    "REDDIT_CLIENT_SECRET": os.getenv("REDDIT_CLIENT_SECRET"),
    "REDDIT_USER_AGENT": os.getenv("REDDIT_USER_AGENT"),
    "YOUTUBE_API_KEY": os.getenv("YOUTUBE_API_KEY"),
    "YOUTUBE_TOPICS": ['large language models', 'LLM', 'AI tools', 'LLM tutorials'],
    "MEDIUM_TOPICS": ["llm", "large-language-models"],
    "MEDIUM_RELATED_TAGS": [
        "data-science", "prompt-engineering", "mathematical-reasoning", 
        "nlp", "time-series", "text-generation", "artificial-intelligence", "ai"
    ],
    "REDDIT_CHANNELS": ['LocalLLaMA', 'GPT3', 'MachineLearning', 'MistralAI', 'OpenAI'],
    "DAYS_BACK": 1,
    "DB_NAME": "ai_news.db"
}


def save_to_sqlite(df: pd.DataFrame, table_name: str, db_name: str, id_column: str):
    """
    Append new data to a SQLite database table, avoiding duplicates.
    If the table doesn't exist, it will be created.
    """
    conn = sqlite3.connect(db_name)
    
    # Check if the table exists
    cursor = conn.cursor()
    cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
    table_exists = cursor.fetchone() is not None
    
    if table_exists:
        # Read existing data
        existing_df = pd.read_sql(f"SELECT * FROM {table_name}", conn)
        
        # Identify new records
        new_records = df[~df[id_column].isin(existing_df[id_column])]
        
        # Append only new records
        new_records.to_sql(table_name, conn, if_exists='append', index=False)
        print(f"Appended {len(new_records)} new records to {table_name}")
    else:
        # If the table doesn't exist, create it with all records
        df.to_sql(table_name, conn, if_exists='replace', index=False)
        print(f"Created new table {table_name} with {len(df)} records")
    
    conn.close()


def filename_generator(dst_dir="news"):
    today = datetime.now().strftime("%Y-%m-%d")
    os.makedirs(dst_dir, exist_ok=True)

    today = datetime.now().strftime("%Y-%m-%d")
    filename = f"AI_News_Summary_{today}.md"
    path_to_fname = os.path.join(dst_dir, filename)
    ix = 0
    while os.path.exists(path_to_fname):
        ix += 1
        filename = f"AI_News_Summary_{today}_{ix:02d}.md"
        path_to_fname = os.path.join(dst_dir, filename)
    
    return path_to_fname

    
def generate_markdown(dst_dir, 
                      techcrunch_articles: List[TechCrunchArticle], 
                      youtube_videos: List[Video], 
                      reddit_posts: List[RedditPost], 
                      medium_posts: List[MediumArticle]):
    """
    Generates a markdown file summarizing AI news from various sources.
    """
    filename = filename_generator(dst_dir)
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"# AI News Summary - {today}\n\n")
        
        f.write(f"\n## TechCrunch Articles\n")
        for article in techcrunch_articles:
            f.write(f"- [{article.title}]({article.link})\n")
            f.write(f"  - Author: {article.author}\n")
            f.write(f"  - Date: {article.date}\n")
            f.write(f"  - Excerpt: {article.snippet}\n\n")
        
        f.write(f"\n## YouTube Videos\n")
        for video in youtube_videos:
            f.write(f"- [{video.title}]({video.link})\n")
            f.write(f"  - Channel: {video.channel}\n")
            f.write(f"  - Topic: {video.topic}\n")
            f.write(f"  - Published: {video.published_at}\n\n")

        f.write(f"\n## Reddit Posts\n")
        for post in reddit_posts:
            f.write(f"- [{post.title}]({post.url})\n")
            f.write(f"  - Subreddit: r/{post.subreddit}\n")
            f.write(f"  - Author: u/{post.author}\n")
            f.write(f"  - Score: {post.score}\n")
            f.write(f"  - Comments: {post.num_comments}\n")
            f.write(f"  - Date: {post.date}\n\n")

        f.write(f"\n## Medium.com Posts\n")
        for post in medium_posts:
            f.write(f"- [{post.title}]({post.link})\n")
            f.write(f"  - Topic: {post.topic}\n")
            f.write(f"  - Date: {post.date}\n")
            f.write(f"  - Excerpt: {post.snippet}\n\n")
            if post.img:
                f.write(f"  ![Article Image]({post.img})\n\n")

    print(f"Markdown file '{filename}' has been generated.")


def main():
    # Initialize fetchers
    reddit_fetcher = RedditNewsFetcher(
        CONFIGS["REDDIT_CHANNELS"],
        CONFIGS["REDDIT_CLIENT_ID"],
        CONFIGS["REDDIT_CLIENT_SECRET"],
        CONFIGS["REDDIT_USER_AGENT"],
        CONFIGS["DAYS_BACK"]
    )
    
    youtube_fetcher = YouTubeNewsFetcher(
        CONFIGS["YOUTUBE_API_KEY"],
        CONFIGS["YOUTUBE_TOPICS"],
        CONFIGS["DAYS_BACK"]
    )
    
    techcrunch_fetcher = TechCrunchNews(CONFIGS["DAYS_BACK"])
    
    medium_fetcher = MediumNewsFetcher(
        CONFIGS["MEDIUM_TOPICS"],
        CONFIGS["MEDIUM_RELATED_TAGS"],
        CONFIGS["DAYS_BACK"]
    )

    # Fetch content
    print("Fetching Reddit posts...")
    reddit_posts = reddit_fetcher.fetch_posts()
    
    print("Fetching YouTube videos...")
    youtube_videos = [] #youtube_fetcher.fetch_videos()
    
    print("Fetching TechCrunch articles...")
    techcrunch_articles = techcrunch_fetcher.get_articles()
    
    print("Fetching Medium posts...")
    medium_posts = medium_fetcher.fetch_articles()

    # Convert to DataFrames and save to SQLite
    reddit_df = pd.DataFrame([vars(post) for post in reddit_posts])
    save_to_sqlite(reddit_df, 'reddit_posts', CONFIGS["DB_NAME"], "link")

    youtube_df = pd.DataFrame([vars(video) for video in youtube_videos])
    save_to_sqlite(youtube_df, 'youtube_videos', CONFIGS["DB_NAME"], "link")

    techcrunch_df = pd.DataFrame([vars(article) for article in techcrunch_articles])
    save_to_sqlite(techcrunch_df, 'techcrunch_articles', CONFIGS["DB_NAME"], "link")

    medium_df = pd.DataFrame([vars(post) for post in medium_posts])
    save_to_sqlite(medium_df, 'medium_posts', CONFIGS["DB_NAME"], "link")

    # Print summary
    print("\n--- Content Fetching Summary ---")
    print(f"Reddit posts: {len(reddit_posts)}")
    print(f"YouTube videos: {len(youtube_videos)}")
    print(f"TechCrunch articles: {len(techcrunch_articles)}")
    print(f"Medium posts: {len(medium_posts)}")
    print("--------------------------------")

    # Generate markdown
    generate_markdown("news", techcrunch_articles, youtube_videos, reddit_posts, medium_posts)

    print(f"All data has been saved to {CONFIGS['DB_NAME']}")


if __name__ == "__main__":
    main()