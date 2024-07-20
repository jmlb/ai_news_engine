import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

from tools.reddit_search import LLM_News_From_Reddit
from tools.techcrunch_search import TechCrunchNews
from tools.youtube_search import LLM_News_From_Youtube
from tools.mediumposts_news import get_latest_medium_posts

# Load environment variables from a .env file
load_dotenv()
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT")
API_KEY = os.getenv("YOUTUBE_API_KEY")

# Topics
YOUTUBE_TOPICS = ['large language models', 'LLM', 'AI tools', 'LLM tutorials']
MEDIUM_TOPICS = ["llm", "large-language-models"]
MEDIUM_RELATED_TAGS = ["data-science", "prompt-engineering", "mathematical-reasoning", 
                       "nlp", "time-series", "text-generation", "artificial-intelligence", "ai"]
TECHCRUNCH_TOPICS =  ["large language models", "AI", "artificial intelligence", "machine learning"]
REDDIT_CHANNELS = ['LocalLLaMA', 'GPT3', 'MachineLearning', 'MistralAI', 'OpenAI']


def generate_markdown(techcrunch_articles, youtube_videos, reddit_posts, medium_posts):
    """
    Generates a markdown file summarizing AI news from various sources.

    Args:
        techcrunch_articles (list): List of articles from TechCrunch.
        youtube_videos (list): List of YouTube videos.
        reddit_posts (list): List of Reddit posts.
        medium_posts (list): List of Medium posts.
    """
    today = datetime.now().strftime("%Y-%m-%d")
    filename = f"{today}.md"
    filepath = os.path.join("daily_news", filename)
    file_ix = 0
    while os.path.exists(filepath):
        file_ix += 1
        filename = f"{today}_{file_ix:02d}.md"
        filepath = os.path.join("daily_news", filename)


    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f"# AI News Summary - {today}\n\n")
        
        f.write(f"\n## TechCrunch Articles\n")
        for article in techcrunch_articles:
            f.write(f"- [{article['title']}]({article['link']})\n")
            f.write(f"  - Date: {article['date'].strftime('%Y-%m-%d %H:%M:%S %Z')}\n")
            f.write(f"  - Excerpt: {article['excerpt']}\n\n")
        
        f.write(f"\n## YouTube Videos\n")
        for video in youtube_videos:
            f.write(f"- [{video['title']}]({video['link']})\n")
            f.write(f"  - Channel: {video['channel']}\n")
            f.write(f"  - Date: {video['date']}\n")
            f.write(f"  - Topic: {video['topic']}\n\n")

        f.write(f"\n## Reddit Posts\n")
        for post in reddit_posts:
            print(post)
            f.write(f"- [{post['title']}]({post['link']})\n")
            f.write(f"  - num comments: r/{post['num_comments']}\n")
            f.write(f"  - Subreddit: r/{post['subreddit']}\n")

        f.write(f"\n## Medium.com Posts\n")
        f.write("<ul>")
        for post in medium_posts:
            f.write('<li style="margin-bottom: 10px;">')
            img_src = post["img"]
            f.write(f'<img src="{img_src}" alt="Image" style="width:100px; float:left; margin-right:10px;" />')
            f.write(f'<a href="{post["link"]}">{post["title"]}</a><br>')
            f.write(f'<strong>Summary:</strong> {post["snippet"]}<br>')
            f.write(f'<strong>Topic:</strong> {post["topic"]}<br>')
            f.write('<div style="clear:both;"></div>')
            f.write('</li>')
            f.write('<br>')
        f.write("</ul>")
            
    print(f"Markdown file '{filename}' has been generated.")


def main():
    """Main function to fetch news from various sources and generate a markdown summary."""
    
    reddit_news_engine = LLM_News_From_Reddit(REDDIT_CHANNELS, REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT)
    youtube_news_engine = LLM_News_From_Youtube(YOUTUBE_TOPICS, API_KEY)
    techcrunch_news_engine = TechCrunchNews(TECHCRUNCH_TOPICS)

    #try:
    reddit_posts = reddit_news_engine()
    techcrunch_articles = techcrunch_news_engine()
    youtube_videos = youtube_news_engine()

    medium_posts = get_latest_medium_posts(MEDIUM_TOPICS, MEDIUM_RELATED_TAGS)

    print("Number of youtube ", len(youtube_videos))
    print("Number of Reddit ", len(reddit_posts))
    print("Number of techCrunch ", len(techcrunch_articles))
    print("Number of Medium.com ", len(medium_posts))
  
    generate_markdown(techcrunch_articles, youtube_videos, reddit_posts, medium_posts)


if __name__ == "__main__":
    main()
