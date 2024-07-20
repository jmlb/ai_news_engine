import re
import time
import json
from langdetect import detect
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class LatestMediumPosts:
    """
    Class to scrape and process Medium articles based on given topics.
    """
    def __init__(self, topics, verbose=False):
        self.url = "https://medium.com"
        self.topics = topics
        self.verbose = verbose
        self.driver = self.initialize_driver()

    def initialize_driver(self,):
        """
        Initialize the WebDriver with Chrome options.
        """
        options = webdriver.ChromeOptions()
        #options.add_argument('--headless=new')
        options.add_argument('--disable-gpu')
        #options.add_argument('--no-sandbox')
        #options.add_argument('--disable-dev-shm-usage')


        return webdriver.Chrome(options=options)

    def extract_post_age(self, article):
        """
        Extract the age of the post from the article.
        """
        divs = article.find_all("div")
        div_texts = [x.get_text(strip=True) for x in divs]
        div_texts = [x for x in div_texts if isinstance(x, str)]
        div_texts = [self.replace_just_now(x) for x in div_texts]

        ages = []
        for x in div_texts:
            m = self.extract_time_ago(x)
            if len(m) > 0:
                ages += m

        ages = [x for x in list(set(ages)) if len(x) > 0]
        age = None
        if len(ages) > 0:
            age = ages[0]
        
        return age
    
    @staticmethod
    def extract_time_ago(input_str):
        """
        Extract time information from a string using regex.
        """
        pattern = r'\b\d{1,2}[hd] ago'
        # Find all matches in the input string
        matches = re.findall(pattern, input_str)
        return matches

    @staticmethod
    def replace_just_now(input_str):
        """
        Replace 'just now' with '0h ago' for consistency in age extraction.
        """
        return "0h ago" if input_str.lower() == "just now" else input_str

    def extract_links(self, this_article):
        """
        Extract links from the article.
        """
        data_href = [a.get('data-href') for a in this_article.find_all('div') if a.get('data-href')]
        links = [x for x in data_href if len(x) > 0 and "https" in x]
        link = None
        if len(links) > 0:
           link = links[0]
        
        if self.verbose and isinstance(link, None):
            print("Failed link extraction: ", data_href)

        return link

    def extract_snippet(self, this_article):
        """
        Extract snippet text from the article.
        """
        h3s = this_article.find_all('h3')
        h3_texts_ = [h3.get_text(strip=True) for h3 in h3s]
        h3_texts = [x for x in h3_texts_ if len(x) > 0]

        snippet = None
        if len(h3_texts) > 0:
            snippet = h3_texts[0]
                
        if self.verbose and isinstance(snippet, type(None)):
            print("Failed snippet extract ", h3_texts_)

        return snippet

    def extract_title(self, this_article):
        """
        Extract title from the article.
        """
        h2s = this_article.find_all('h2')
        h2_texts = [h2.get_text(strip=True) for h2 in h2s]
        h2_texts = [x for x in h2_texts if len(x) > 0]
        
        aria_labels = [x.get("aria-label") for x in this_article.find_all('div')]
        titles = [x for x in aria_labels if isinstance(x, str) and len(x) > 0]
        titles += h2_texts

        title = None
        if len(titles) > 0:
            title = titles[0]

        if self.verbose and isinstance(title, type(None)):
            print("Failed title extract ", h2_texts)
            print("Failed title extract ", aria_labels)

        return title

    def extract_image(self, this_article):
        """
        Extract image URLs from the article.
        """
        srcs = list(set([x.get("src") for x in this_article.find_all('img')]))
        imgs = [img for img in srcs if ".jpg" in img.lower() or ".png" in img.lower() or ".jpeg" in img.lower()]
        img = None
        if len(imgs) > 0:
            img = imgs[0]
        
        if self.verbose and isinstance(img, type(None)):
            print("Failed image extract ", srcs)

        return img 

    def parse_article(self, this_article):
        """
        Parse the article to extract relevant information.
        """
        return {"title": self.extract_title(this_article), 
                "link": self.extract_links(this_article), 
                "img": self.extract_image(this_article), 
                "snippet": self.extract_snippet(this_article), 
                "post_age": self.extract_post_age(this_article)}


    @staticmethod    
    def is_longer_than_1_day(age_str):
        """
        Check if the age string indicates a time longer than 1 day.
        """
        return 'd ago' in age_str

    # # Define a function to extract articles
    def extract_articles(self, ):
        """
        Extract articles from the current page source.
        """
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        articles = soup.find_all('article')
        article_data = []
        for article in articles:
            post = self.parse_article(article)
            try:
                if detect(post["title"]) != "en":
                    continue
            except:
                continue
            article_data.append(post)
        return article_data

    @staticmethod
    def remove_duplicate_posts(posts):
        """
        Remove duplicate articles based on their links.
        """
        unique_posts = []
        seen_links = []
        for p in posts:
            if p['link'] not in seen_links:
                unique_posts.append(p)
                seen_links.append(p['link'])

        return unique_posts

    def run(self,):
        """
        Main method to run the scraping process.
        """
        posts = []
        ntopics = len(self.topics)
        for ix, topic in enumerate(self.topics):
            print(f"- Retrieve Latest posts from topic: {topic} ({ix+1}/{ntopics}) | number of retrieved posts: ", end="")
            # URL of the Medium tag page
            url = f"https://medium.com/tag/{topic}/archive"
            self.driver.get(url)

            # Wait until the page is fully loaded
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))

            run = True
            n_prev_articles = 0

            while run:  # Condition to stop scrolling
                articles = self.extract_articles()

                for ix, article in enumerate(articles):
                    age = article["post_age"]

                    if isinstance(age, str) and self.is_longer_than_1_day(article["post_age"]):
                        continue
                    
                    article["topic"] = topic
                    posts.append(article)

                posts = self.remove_duplicate_posts(posts)
                n_valid_articles = len(posts)
                # No valid posts after first iteration - stop
                print("Valid n articles ", n_valid_articles)
                run = n_valid_articles > n_prev_articles

                n_prev_articles = n_valid_articles

                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)  # Wait for new content to load

        # Close the WebDriver
        self.driver.quit()

        return self.remove_duplicate_posts(posts)
    

def is_valide_post(this_driver, article, subtopics=[]):
    """
    Validate the post by checking if it contains any of the subtopics.
    Args:
        this_driver 
        article
        subtopics
    """
    link = article["link"]
    if not link:
        return False
    
    this_driver.get(link)

    WebDriverWait(this_driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
    soup = BeautifulSoup(this_driver.page_source, 'html.parser')
    tags = soup.find_all('href')
    tags = [tag.get('href') for tag in tags]
    tags = soup.find_all('a', href=True)
    tags = [tag.get('href') for tag in tags]
    tags = [tag for tag in tags if "/tag/" in tag]
    tags = [tag.split("?source=post_page")[0].replace("/tag/", "") for tag in tags]
    match_tags = [tag for tag in tags if tag.strip() in subtopics]
    time.sleep(1)  # Wait for new content to load
    return len(match_tags) > 1


def get_latest_medium_posts(topics, all_tags):
    """
    Retrieve the latest Medium posts for given topics and filter them by subtopics.
    """
    all_tags_ = all_tags + topics
    latest_posts_engine = LatestMediumPosts(topics)
    latest_posts = latest_posts_engine.run()
    print(f"\nTotal Number of Latest posts: {len(latest_posts)}")

    # driver = latest_pubs_engine.initialize_driver()
    valid_posts = []
    driver = latest_posts_engine.initialize_driver()
    for ix, post in enumerate(latest_posts):
        if ix%200 == 0:
            driver.quit()
            time.sleep(2)
            driver = latest_posts_engine.initialize_driver()
        if is_valide_post(driver, post, all_tags_):
            valid_posts.append(post)

    driver.quit()

    print(f"Total Number of valid posts: {len(valid_posts)}")
    
    return valid_posts


if __name__ == "__main__":
    interests = ["llm", "large-language-models"]
    related_tags = ["data-science", "prompt-engineering", "mathematical-reasoning", 
                    "nlp", "time-series", "text-generation", "artificial-intelligence", "ai"]

    posts = get_latest_medium_posts(interests, related_tags)
    
    with open("medium.json", "w") as f:
        json.dump(posts, f, indent=1)
