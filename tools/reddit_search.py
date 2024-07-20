import os
import praw
from dotenv import load_dotenv
from datetime import datetime, timezone


load_dotenv()
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT")


class LLM_News_From_Reddit:
    """
    A class to fetch today's posts from specified subreddits related to large language models (LLMs).
    """

    def __init__(self, subreddits, client_id="", client_secret="", user_agent=""):
        """
        Initialize the LLM_News_From_Reddit instance with Reddit API credentials.
        
        Args:
            subredits (list)
            client_id (str): Reddit client ID.
            client_secret (str): Reddit client secret.
            user_agent (str): Reddit user agent.
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.user_agent = user_agent
        # List of subreddits to fetch posts from
        self.subreddits = subreddits

    def init_reddit_client(self,):
        """
        Initialize and return a Reddit client instance.
        
        Returns:
            praw.Reddit: Reddit client instance.
        """
        return praw.Reddit(
            client_id=self.client_id,
            client_secret=self.client_secret,
            user_agent=self.user_agent
        )

    @staticmethod
    def is_today(timestamp):
        """
        Check if the given timestamp is from today.
        
        Args:
            timestamp (int): Unix timestamp.
        
        Returns:
            bool: True if the timestamp is from today, False otherwise.
        """
        post_date = datetime.fromtimestamp(timestamp, tz=timezone.utc)
        today = datetime.now(timezone.utc)
        return post_date.date() == today.date()


    def fetch_today_posts(self, reddit, subreddit_name):
        """
        Fetch today's posts from a specific subreddit.
        
        Args:
            reddit (praw.Reddit): Reddit client instance.
            subreddit_name (str): Name of the subreddit.
        
        Returns:
            list: List of dictionaries containing post details.
        """
        subreddit = reddit.subreddit(subreddit_name)
        today_posts = []
        print(subreddit)
        for post in subreddit.new(limit=None):
            if self.is_today(post.created_utc):
                today_posts.append({
                    'title': post.title,
                    'url': f"https://www.reddit.com{post.permalink}",
                    'author': post.author.name if post.author else '[deleted]',
                    'score': post.score,
                    'num_comments': post.num_comments
                })
            else:
                # If we've reached posts from yesterday, stop fetching
                break

        return today_posts

    def __call__(self,):
        """
        Fetch today's posts from all specified subreddits and return a list of post details.
        
        Returns:
            list: List of dictionaries containing post details from all subreddits.
        """
        reddit = self.init_reddit_client()
        all_posts = {}

        for subreddit in self.subreddits:
            #print(f"Fetching posts from r/{subreddit}...")
            all_posts[subreddit] = self.fetch_today_posts(reddit, subreddit)
            #print(f"Found {len(all_posts[subreddit])} posts in r/{subreddit}")

        # Generate a simple report
        # print("\nToday's AI-related posts:")
        reddit_posts = []
        for subreddit, posts in all_posts.items():
            for post in posts:
                reddit_posts.append({"title": post['title'],
                                     "subreddit": subreddit,
                                     "score": post['score'],
                                     "num_comments": post['num_comments'],
                                     "link": post["url"]})

        print("Reddit posts ", reddit_posts)
        return reddit_posts


if __name__ == "__main__":

    subreddits = ['LocalLLaMA', 'GPT3', 'MachineLearning', 'MistralAI', 'OpenAI']
    rnews = LLM_News_From_Reddit(subreddits, REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT)
    posts = rnews()
    
    print(posts)