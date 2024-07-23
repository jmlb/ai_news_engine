"""
YouTube AI News Fetcher

This script fetches YouTube videos related to large language models and AI tools.
It uses the YouTube Data API to search for videos and retrieve their details.

Usage:
    python youtube_ai_fetcher.py

Dependencies:
    - google-api-python-client
    - python-dotenv

Author: Jean-Marc Beaujour
Date: July 21, 2024
Version: 2.0
License: MIT
"""

import os
from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from dotenv import load_dotenv
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from youtube_transcript_api import YouTubeTranscriptApi
from pytube import YouTube


# Load environment variables
load_dotenv()


@dataclass
class Video:
    title: str
    video_id: str
    published_at: str
    topic: str
    link: str
    channel: str
    date: str
    description: str
    transcript: str


class YouTubeAPIClient:
    def __init__(self, api_key: str):
        self.youtube = build('youtube', 'v3', developerKey=api_key)

    def search_videos(self, query: str, published_after: str, max_results: int = 50) -> List[Dict]:
        try:
            search_response = self.youtube.search().list(
                q=query,
                type='video',
                part='id,snippet',
                maxResults=max_results,
                publishedAfter=published_after,
                relevanceLanguage='en',
                order='date'
            ).execute()

            return search_response.get('items', [])
        except HttpError as e:
            print(f'An HTTP error {e.resp.status} occurred:\n{e.content}')
            return []


class VideoProcessor:
    def __init__(self):
        pass
    
    def process_video(self, video_item: Dict, query: str) -> Video:
        snippet = video_item['snippet']
        video_id = video_item['id']['videoId']
        link = f"https://www.youtube.com/watch?v={video_id}"

        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            transcript = self.process_raw_transcript(transcript)
        except:
            transcript = ""

        video = YouTube(link)
        description = video.description

        return Video(
            title=snippet['title'],
            video_id=video_id,
            published_at=snippet['publishedAt'],
            topic=query,
            link=link,
            channel=snippet['channelTitle'],
            date=snippet['publishedAt'],
            description=description,
            transcript=transcript
        )
    
    @staticmethod
    def process_raw_transcript(raw_transcript):
        transcript_txt = ""
        for segment in raw_transcript:
            transcript_txt = transcript_txt +" "+ segment["text"]

        return transcript_txt
    

class YouTubeNewsFetcher:
    def __init__(self, api_key: str, search_terms: List[str], days_back: int = 1):
        self.api_client = YouTubeAPIClient(api_key)
        self.search_terms = search_terms
        self.days_back = days_back

    def get_published_after_date(self) -> str:
        date = datetime.utcnow() - timedelta(days=self.days_back)
        return date.replace(hour=0, minute=0, second=0, microsecond=0).isoformat() + 'Z'

    def fetch_videos(self) -> List[Video]:
        published_after = self.get_published_after_date()
        video_processor = VideoProcessor()
        all_videos = []

        for term in self.search_terms:
            video_items = self.api_client.search_videos(term, published_after)
            videos = [video_processor.process_video(video_item=item, query=term) for item in video_items]
            all_videos.extend(videos)

        return self.remove_duplicates(all_videos)

    @staticmethod
    def remove_duplicates(videos: List[Video]) -> List[Video]:
        unique_videos = {v.video_id: v for v in videos}.values()
        return sorted(unique_videos, key=lambda x: x.published_at, reverse=True)


def main(topics = ['large language models', 'LLM', 'AI tools', 'LLM tutorials'],
         days_back=1):
    api_key = os.getenv("YOUTUBE_API_KEY")
    if not api_key:
        raise ValueError("YouTube API key not found in environment variables")

    fetcher = YouTubeNewsFetcher(api_key, topics, days_back)
    videos = fetcher.fetch_videos()

    print(f"\nTotal unique videos found: {len(videos)}")
    for video in videos:
        print(f"Title: {video.title}")
        print(f"Channel: {video.channel}")
        print(f"Topic: {video.topic}")
        print(f"Link: {video.link}")
        print(f"Published at: {video.published_at}")
        print(f"Description: {video.description}")
        print(f"Transcript: {video.transcript}")
        print("---")

    return videos


if __name__ == "__main__":
    main()