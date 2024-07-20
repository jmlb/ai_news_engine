import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError



load_dotenv()
API_KEY = os.getenv("YOUTUBE_API_KEY")


class LLM_News_From_Youtube:
    """
    A class to fetch YouTube videos related to large language models and AI tools.

    Attributes:
        api_key (str): YouTube API key for authentication.
        search_terms (list): List of search terms to query on YouTube.

    Methods:
        get_authenticated_service(): Returns an authenticated YouTube service object.
        iso_format_today(): Returns the current date in ISO format.
        search_videos(youtube, query, published_after): Searches for videos on YouTube based on the query and date.
        __call__(): Fetches and returns a list of unique videos for the given search terms.
    """
    def __init__(self, search_terms, api_key):
        """
        Initializes the LLM_News_From_Youtube class with the provided API key.
        """
        self.api_key = api_key
        self.search_terms = search_terms

    def get_authenticated_service(self,):
        """
        Authenticates and returns the YouTube service object.

        Returns:
            youtube: Authenticated YouTube service object.
        """
        return build('youtube', 'v3', developerKey=self.api_key)

    @staticmethod
    def iso_format_today():
        """
        Returns the current date in ISO 8601 format.

        Returns:
            str: Current date in ISO 8601 format.
        """
        return datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0).isoformat() + 'Z'

    @staticmethod
    def search_videos(youtube, query, published_after):
        """
        Searches for videos on YouTube based on the query and published date.

        Args:
            youtube: Authenticated YouTube service object.
            query (str): Search query string.
            published_after (str): Date in ISO 8601 format to filter videos.

        Returns:
            list: List of dictionaries containing video details.
        """
        try:
            search_response = youtube.search().list(
                q=query,
                type='video',
                part='id,snippet',
                maxResults=50,
                publishedAfter=published_after,
                relevanceLanguage='en',
                order='date'
            ).execute()

            videos = [
                {
                    'title': item['snippet']['title'],
                    'video_id': item['id']['videoId'],
                    'published_at': item['snippet']['publishedAt'],
                    'channel_title': item['snippet']['channelTitle'],
                    'topic': query
                }
                for item in search_response.get('items', [])
            ]

            return videos

        except HttpError as e:
            print(f'An HTTP error {e.resp.status} occurred:\n{e.content}')
            return []

    def __call__(self,):
        """
        Fetches and returns a list of unique videos for the given search terms.

        Returns:
            list: List of dictionaries containing unique video details.
        """
        youtube = self.get_authenticated_service()
        published_after = self.iso_format_today()

        all_videos = []

        for term in self.search_terms:
            #print(f"Searching for videos about '{term}'...")
            videos = self.search_videos(youtube, term, published_after)
            all_videos.extend(videos)

        # Remove duplicates and sort videos by published date
        unique_videos = list({v['video_id']:v for v in all_videos}.values())
        unique_videos.sort(key=lambda x: x['published_at'], reverse=True)

        for ix, video in enumerate(unique_videos):
            video["link"] = f"https://www.youtube.com/watch?v={video['video_id']}"
            video["channel"] = video['channel_title']
            video["date"] = video['published_at']
            video["topic"] = video["topic"]
            unique_videos[ix] = video

        print(f"\nTotal unique videos found: {len(unique_videos)}")

        return unique_videos


if __name__ == '__main__':
    topics = ['large language models', 'LLM', 'AI tools', 'LLM tutorials']
    youtube_news = LLM_News_From_Youtube(topics, API_KEY)
    youtube_news()