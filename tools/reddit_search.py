"""
Reddit AI News Fetcher

This script fetches recent posts from specified subreddits related to AI and large language models.
It uses the PRAW (Python Reddit API Wrapper) to interact with Reddit's API.

Usage:
    python reddit_ai_fetcher.py

Dependencies:
    - praw
    - python-dotenv

Author: Jean-Marc Beaujour (Improved by Assistant)
Date: July 21, 2024
Version: 2.0
License: MIT
"""

import os
from typing import List, Dict, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
from dotenv import load_dotenv
import praw


# Load environment variables
load_dotenv()


@dataclass
class RedditPost:
    title: str
    link: str
    author: str
    score: int
    date: str
    content: str
    num_comments: int
    subreddit: str
    is_self: bool


class RedditAPIClient:
    def __init__(self, client_id: str, client_secret: str, user_agent: str):
        self.reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent
        )

    def fetch_posts(self, subreddit_name: str, time_window: List[str]) -> List[Dict[str, Any]]:
        subreddit = self.reddit.subreddit(subreddit_name)
        recent_posts = []

        for post in subreddit.new(limit=None):
            post_date = datetime.fromtimestamp(post.created_utc).strftime('%Y-%m-%d')
            link = f"https://www.reddit.com{post.permalink}"
            if post_date in time_window:
                recent_posts.append({
                    'title': post.title,
                    'link': link,
                    'author': post.author.name if post.author else '[deleted]',
                    'score': post.score,
                    'date': post_date,
                    'content': post.selftext if post.is_self else link,
                    'num_comments': post.num_comments,
                    'subreddit': subreddit_name,
                    'is_self': post.is_self
                })
            elif post_date < min(time_window):
                break  # Stop if we've reached posts older than our time window

        return recent_posts

class PostProcessor:
    @staticmethod
    def process_post(post: Dict[str, Any]) -> RedditPost:
        return RedditPost(
            title=post['title'],
            link=post['link'],
            author=post['author'],
            score=post['score'],
            date=post['date'],
            num_comments=post['num_comments'],
            subreddit=post['subreddit'],
            content=post['content'],
            is_self=post['is_self']
        )

class RedditNewsFetcher:
    def __init__(self, subreddits: List[str], client_id: str, client_secret: str, user_agent: str, days_back: int = 1):
        self.api_client = RedditAPIClient(client_id, client_secret, user_agent)
        self.subreddits = subreddits
        self.days_back = days_back
        self.time_window = self.generate_time_window()

    def generate_time_window(self) -> List[str]:
        today = datetime.now().date()
        return [(today - timedelta(days=x)).strftime("%Y-%m-%d") for x in range(self.days_back)]

    def fetch_posts(self) -> List[RedditPost]:
        all_posts = []

        for subreddit in self.subreddits:
            print(f"Fetching posts from r/{subreddit}")
            raw_posts = self.api_client.fetch_posts(subreddit, self.time_window)
            processed_posts = [PostProcessor.process_post(post) for post in raw_posts]
            all_posts.extend(processed_posts)

        return sorted(all_posts, key=lambda x: x.date, reverse=True)

def main(subreddits = ['LocalLLaMA', 'GPT3', 'MachineLearning', 'MistralAI', 'OpenAI'], days_back=1):
    client_id = os.getenv("REDDIT_CLIENT_ID")
    client_secret = os.getenv("REDDIT_CLIENT_SECRET")
    user_agent = os.getenv("REDDIT_USER_AGENT")

    if not all([client_id, client_secret, user_agent]):
        raise ValueError("Reddit API credentials not found in environment variables")

    fetcher = RedditNewsFetcher(subreddits, client_id, client_secret, user_agent, days_back)
    posts = fetcher.fetch_posts()

    print(f"\nTotal posts found: {len(posts)}")
    for post in posts:
        print(f"title: {post.title}")
        print(f"subreddit: r/{post.subreddit}")
        print(f"author: u/{post.author}")
        print(f"score: {post.score}")
        print(f"comments: {post.num_comments}")
        print(f"date: {post.date}")
        print(f"link: {post.link}")
        if post.is_self:
            print(f"Content: {post.content}")
        print("---")

    return posts


if __name__ == "__main__":
    main()