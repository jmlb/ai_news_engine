# AI News Engine


## 1. AI News Aggregator
This Python script aggregates AI-related news from various sources, generates a summary in Markdown format, and stores the data in a SQLite database.
Collects news from multiple platforms:

    - TechCrunch articles
    - YouTube videos
    - Reddit posts
    - Medium.com articles

The content is filtered based on AI-related topics and channels. The script can aggregate daily data or data from the last `n` days. The user can choose the number of days back from today by editing the `DAYS_BACK` value in the `CONFIGS` dictionary in `main.py`.

### 1.1 Configuration
The script uses environment variables for API keys and defines topics and channels to monitor (edit `.env` to enter your own API keys).
The results are displayed in a markdown file with the name of the day of the data query and are saved in the sub-directory `./news`.

### 1.2 Usage

Install the required dependencies:

```
pip install praw google-api-python-client selenium beautifulsoup4 langdetect python-dotenv pandas
```

Set up your `.env` file with the necessary API keys:
```
REDDIT_CLIENT_ID=<your_reddit_client_id>
REDDIT_CLIENT_SECRET=<your_reddit_client_secret>
REDDIT_USER_AGENT=<your_reddit_user_agent>
YOUTUBE_API_KEY=<your_youtube_api_key>
```

Run the script:
```
python main.py
```

### 1.3 Customization
You can modify the CONFIGS dictionary in `main.py` to:

    - Adjust the list of Reddit channels
    - Change YouTube search topics
    - Update Medium tags and topics
    - Alter the number of days to look back for content
    - Change the SQLite database name

### 1.4 Data Storage
The script now stores all fetched data in a SQLite database. It appends new data to existing tables, avoiding duplicates. The database contains four tables:

    - reddit_posts
    - youtube_videos
    - techcrunch_articles
    - medium_posts


## 2. Tools

### 2.1 Medium Posts Scraper
The Medium Posts Scraper has been improved with better organization and error handling. It now uses a `MediumNewsFetcher` class that encapsulates the scraping logic.

#### 2.1.1 Key Features

    - Uses Selenium WebDriver for dynamic page loading
    - Implements scrolling to load more articles
    - Filters articles based on publication date and language
    - Avoids duplicate articles

#### 2.1.2 Usage
Modify the interests and related_tags lists in the `main()` function of `mediumposts_search.py` to customize your search.

### 2.2 YouTube Posts Scraper
The YouTube scraper now uses a YouTubeNewsFetcher class for better organization.

#### 2.2.1 Key Features

    - Uses the YouTube Data API for efficient searching
    - Filters videos based on publication date
    - Removes duplicate results
    - Sorts videos by publication date

#### 2.2.2 Usage
Modify the `YOUTUBE_TOPICS` list in the `CONFIGS` dictionary of `main.py` to customize your search terms.

### 2.3 Reddit Posts Scraper
The Reddit scraper has been refactored into a RedditNewsFetcher class for improved modularity.

#### 2.3.1 Key Features

    - Fetches posts from multiple subreddits
    - Configurable time window
    - Collects comprehensive post details

#### 2.3.2 Usage
Modify the `REDDIT_CHANNELS` list in the `CONFIGS` dictionary of `main.py` to customize the subreddits to scrape.

### 2.4 TechCrunch Search Engine
The TechCrunch scraper has been reorganized into a `TechCrunchNews` class for better structure.

#### 2.4.1 Key Features

    - Scrapes articles from TechCrunch's AI category
    - Retrieves article links, author names, snippets, and publication dates
    - Allows customization of the time frame for article retrieval

#### 2.4.2 Usage
The TechCrunch scraper is automatically used when running `main.py`. You can adjust the `DAYS_BACK` value in the `CONFIGS` dictionary to change the time frame for article retrieval.

## 3. Data Persistence
All scraped data is now stored in a SQLite database (`ai_news.db` by default). The script appends new data to existing tables, avoiding duplicates. This allows for accumulating data over time and enables more complex data analysis tasks.

## 4. Error Handling and Logging
The script now includes improved error handling and logging. It will continue running even if one source fails, ensuring you get as much data as possible.

Note
This script is designed for educational and research purposes. Make sure to comply with the terms of service and rate limiting guidelines of all platforms (Reddit, YouTube, Medium, TechCrunch) when using this tool.