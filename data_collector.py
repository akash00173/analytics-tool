import json
import random
from datetime import datetime, timedelta
from typing import Dict, List
import tweepy
import praw
import threading
import time
from data_storage import DataStorage
from config import AppConfig, TwitterConfig, YouTubeConfig


class TwitterDataCollector:
    """
    Simulates Twitter API data collection
    In a real implementation, this would connect to the Twitter API
    """

    def __init__(self):
        self.platform = "Twitter"

    def get_posts_data(self, username: str, count: int = 10) -> List[Dict]:
        """Simulate getting tweet data"""
        posts = []
        for i in range(count):
            post = {
                'post_id': f'tweet_{random.randint(10000, 99999)}',
                'username': username,
                'text': f'Sample tweet {i+1} about social media analytics',
                'timestamp': (datetime.now() - timedelta(days=random.randint(0, 30))).isoformat(),
                'likes': random.randint(0, 1000),
                'retweets': random.randint(0, 500),
                'replies': random.randint(0, 100),
                'hashtags': [f'#hashtag{random.randint(1, 20)}', f'#socialmedia'],
                'location': random.choice(['New York', 'London', 'Tokyo', 'San Francisco', 'Berlin'])
            }
            posts.append(post)
        return posts

    def get_user_metrics(self, username: str) -> Dict:
        """Simulate getting user metrics"""
        return {
            'followers': random.randint(1000, 100000),
            'following': random.randint(100, 5000),
            'tweets_count': random.randint(100, 10000),
            'account_age_days': random.randint(100, 3000),
            'engagement_rate': round(random.uniform(1.0, 5.0), 2)
        }


class YouTubeDataCollector:
    """
    Simulates YouTube API data collection
    In a real implementation, this would connect to the YouTube Data API
    """

    def __init__(self):
        self.platform = "YouTube"

    def get_video_data(self, channel_id: str, count: int = 10) -> List[Dict]:
        """Simulate getting video data from a YouTube channel"""
        videos = []
        for i in range(count):
            video = {
                'video_id': f'vid_{random.randint(10000, 99999)}',
                'channel_id': channel_id,
                'title': f'Sample YouTube video {i+1} about social media analytics',
                'description': f'Description for video {i+1}',
                'timestamp': (datetime.now() - timedelta(days=random.randint(0, 30))).isoformat(),
                'views': random.randint(0, 100000),
                'likes': random.randint(0, 10000),
                'comments': random.randint(0, 5000),
                'dislikes': random.randint(0, 500),
                'duration': f'{random.randint(1, 20)}:{random.randint(10, 59)}',
                'tags': [f'tag{random.randint(1, 20)}', 'socialmedia', 'analytics'],
                'category': random.choice(['Education', 'Entertainment', 'Howto & Style', 'Music']),
                'url': f'https://youtube.com/watch?v=video_{random.randint(10000, 99999)}'
            }
            videos.append(video)
        return videos

    def get_channel_metrics(self, channel_id: str) -> Dict:
        """Simulate getting channel metrics"""
        return {
            'subscribers': random.randint(1000, 1000000),
            'total_videos': random.randint(10, 5000),
            'total_views': random.randint(10000, 10000000),
            'channel_age_days': random.randint(100, 3000),
            'engagement_rate': round(random.uniform(2.0, 8.0), 2)
        }


class TwitterAPIDataCollector:
    """
    Real Twitter API data collector
    Uses configuration from config module
    Falls back to simulated data if credentials are not provided
    """

    def __init__(self, config: TwitterConfig = None):
        if config is None:
            # Load from config file if not provided
            app_config = AppConfig.load_from_file()
            config = app_config.twitter

        # Store the configuration
        self.config = config

        # Check if credentials are provided
        if (config.bearer_token and config.bearer_token != "AAAAAAAAAAAAAAAAAAAAAE9I5gEAAAAAiNRbw9qk4ntUmUOgpN8S73fymXY%3DZ9lfIUsu1e8LZsGXbPbhGwnkzG5WKp8RQGbgy3JtH877wADc87" and
            config.api_key and config.api_key != "97DKzt9UYpFNxhgOJy04NP9NW" and
            config.api_secret and config.api_secret != "39c1WZG2ka66zZIk687WcHgw1Fm5wgGsAadTCpsUlhmugXX3YA" and
            config.access_token and config.access_token != "1499087836938657793-rynXx27qkDUn0Oub6T6OjpboLJHtPE" and
            config.access_token_secret and config.access_token_secret != "rOcm5iDXQPDoEFxJQGiQYZ5cNW5bLvA3rfUWf2hpvzHpo"):

            try:
                # Initialize the API client
                self.client = tweepy.Client(
                    bearer_token=config.bearer_token,
                    consumer_key=config.api_key,
                    consumer_secret=config.api_secret,
                    access_token=config.access_token,
                    access_token_secret=config.access_token_secret
                )
                self.use_api = True
                print("Twitter API client initialized with provided credentials")
            except Exception as e:
                print(f"Error initializing Twitter API client: {e}")
                print("Falling back to simulated data collection")
                self.use_api = False
        else:
            print("Twitter API credentials not configured. Using simulated data collection.")
            self.use_api = False

    def get_tweets_by_username(self, username: str, count: int = 10):
        """Get tweets from a specific user"""
        if not self.use_api:
            # Return simulated data if API is not available
            return self._generate_simulated_tweets(username, count)

        try:
            # Get user ID first
            user = self.client.get_user(username=username)
            if not user.data:
                return []

            user_id = user.data.id

            # Get recent tweets from the user
            tweets = self.client.get_users_tweets(
                id=user_id,
                max_results=min(count, 100),  # Twitter API max is 100
                tweet_fields=['created_at', 'public_metrics', 'context_annotations', 'lang']
            )

            if not tweets.data:
                return []

            processed_tweets = []
            for tweet in tweets.data:
                processed_tweet = {
                    'post_id': tweet.id,
                    'username': username,
                    'text': tweet.text,
                    'timestamp': tweet.created_at.isoformat() if tweet.created_at else datetime.now().isoformat(),
                    'likes': tweet.public_metrics['like_count'] if hasattr(tweet, 'public_metrics') else 0,
                    'retweets': tweet.public_metrics['retweet_count'] if hasattr(tweet, 'public_metrics') else 0,
                    'replies': tweet.public_metrics['reply_count'] if hasattr(tweet, 'public_metrics') else 0,
                    'quotes': tweet.public_metrics['quote_count'] if hasattr(tweet, 'public_metrics') else 0,
                    'lang': tweet.lang if hasattr(tweet, 'lang') else 'en'
                }
                processed_tweets.append(processed_tweet)

            return processed_tweets

        except Exception as e:
            print(f"Error fetching tweets for {username}: {e}")
            # Return simulated data as fallback
            return self._generate_simulated_tweets(username, count)

    def search_tweets(self, query: str, count: int = 10):
        """Search for tweets with a specific query"""
        if not self.use_api:
            # Return simulated data if API is not available
            return self._generate_simulated_tweets('user', count)

        try:
            tweets = self.client.search_recent_tweets(
                query=query,
                max_results=min(count, 100),
                tweet_fields=['created_at', 'public_metrics', 'author_id', 'context_annotations']
            )

            if not tweets.data:
                return []

            processed_tweets = []
            for tweet in tweets.data:
                processed_tweet = {
                    'post_id': tweet.id,
                    'text': tweet.text,
                    'timestamp': tweet.created_at.isoformat() if tweet.created_at else datetime.now().isoformat(),
                    'likes': tweet.public_metrics['like_count'] if hasattr(tweet, 'public_metrics') else 0,
                    'retweets': tweet.public_metrics['retweet_count'] if hasattr(tweet, 'public_metrics') else 0,
                    'replies': tweet.public_metrics['reply_count'] if hasattr(tweet, 'public_metrics') else 0,
                    'quotes': tweet.public_metrics['quote_count'] if hasattr(tweet, 'public_metrics') else 0
                }
                processed_tweets.append(processed_tweet)

            return processed_tweets

        except Exception as e:
            print(f"Error searching tweets for query '{query}': {e}")
            # Return simulated data as fallback
            return self._generate_simulated_tweets('user', count)

    def _generate_simulated_tweets(self, username: str, count: int = 10) -> List[Dict]:
        """Generate simulated tweet data when API is not available"""
        tweets = []
        for i in range(count):
            tweet = {
                'post_id': f'sim_tweet_{random.randint(10000, 99999)}_{i}',
                'username': username,
                'text': f'Simulated tweet {i+1} about {username} and social media analytics #hashtag{random.randint(1, 20)}',
                'timestamp': (datetime.now() - timedelta(minutes=random.randint(0, 1440))).isoformat(),  # Within last 24 hours
                'likes': random.randint(0, 100),
                'retweets': random.randint(0, 50),
                'replies': random.randint(0, 20),
                'quotes': random.randint(0, 10),
                'lang': random.choice(['en', 'es', 'fr', 'de'])
            }
            tweets.append(tweet)
        return tweets


class YouTubeAPIDataCollector:
    """
    Real YouTube API data collector
    Uses configuration from config module
    Falls back to simulated data if credentials are not provided
    """

    def __init__(self, config: YouTubeConfig = None):
        if config is None:
            # Load from config file if not provided
            app_config = AppConfig.load_from_file()
            config = app_config.youtube

        # Store the configuration
        self.config = config

        # Check if credentials are provided
        if config.api_key and config.api_key != "AIzaSyAb3A89r-XB2M-6arR_4YHMACB3ca4-wn8":
            # Initialize the YouTube API client
            # For now, we'll use placeholder values
            # In a real implementation, you would initialize the YouTube API client here
            self.use_api = True
            print("YouTube API collector initialized with provided credentials")
        else:
            print("YouTube API key not configured. Using simulated data only.")
            self.use_api = False

    def get_channel_videos(self, channel_id: str, count: int = 10):
        """Get videos from a specific YouTube channel"""
        if not self.use_api:
            # Return simulated data if API is not available
            return self._generate_simulated_videos(channel_id, count)

        try:
            # This is a placeholder implementation
            # In a real implementation, you would call the YouTube API
            print(f"Fetching videos for YouTube channel: {channel_id}")

            # Simulate API response with placeholder data
            videos = []
            for i in range(min(count, 50)):  # YouTube API limits
                video = {
                    'id': f'yt_{random.randint(1000000, 9999999)}',
                    'title': f'YouTube video {i+1} by {channel_id}',
                    'description': f'Description for video {i+1}',
                    'published_at': (datetime.now() - timedelta(hours=random.randint(1, 100))).isoformat(),
                    'view_count': random.randint(100, 100000),
                    'like_count': random.randint(10, 10000),
                    'comment_count': random.randint(0, 1000),
                    'duration': f'PT{random.randint(60, 600)}S',  # ISO 8601 format
                    'thumbnail_url': f'https://example.com/thumbnail_{i}.jpg',
                    'channel_id': channel_id
                }
                videos.append(video)

            return videos

        except Exception as e:
            print(f"Error fetching YouTube videos for {channel_id}: {e}")
            # Return simulated data as fallback
            return self._generate_simulated_videos(channel_id, count)

    def search_videos(self, query: str, count: int = 10):
        """Search for videos with a specific query"""
        if not self.use_api:
            # Return simulated data if API is not available
            return self._generate_simulated_videos('search_result', count)

        try:
            # This is a placeholder implementation
            # In a real implementation, you would call the YouTube API
            print(f"Searching YouTube for query: {query}")

            # Simulate API response with placeholder data
            videos = []
            for i in range(min(count, 50)):  # YouTube API limits
                video = {
                    'id': f'yt_{random.randint(1000000, 9999999)}',
                    'title': f'Search result {i+1} for {query}',
                    'description': f'Description for search result {i+1}',
                    'published_at': (datetime.now() - timedelta(hours=random.randint(1, 50))).isoformat(),
                    'view_count': random.randint(100, 100000),
                    'like_count': random.randint(10, 10000),
                    'comment_count': random.randint(0, 1000),
                    'duration': f'PT{random.randint(60, 600)}S',  # ISO 8601 format
                    'thumbnail_url': f'https://example.com/thumbnail_{i}.jpg',
                    'channel_id': f'channel_{random.randint(1000, 9999)}'
                }
                videos.append(video)

            return videos

        except Exception as e:
            print(f"Error searching YouTube for query {query}: {e}")
            # Return simulated data as fallback
            return self._generate_simulated_videos('search_result', count)

    def _generate_simulated_videos(self, channel_id: str, count: int = 10) -> List[Dict]:
        """Generate simulated video data when API is not available"""
        videos = []
        for i in range(count):
            video = {
                'id': f'sim_yt_{random.randint(1000000, 9999999)}_{i}',
                'title': f'Simulated YouTube video {i+1} by {channel_id}',
                'description': f'Description for simulated video {i+1}',
                'published_at': (datetime.now() - timedelta(hours=random.randint(1, 100))).isoformat(),
                'view_count': random.randint(100, 100000),
                'like_count': random.randint(10, 10000),
                'comment_count': random.randint(0, 1000),
                'duration': f'PT{random.randint(60, 600)}S',  # ISO 8601 format
                'thumbnail_url': f'https://example.com/sim_thumbnail_{i}.jpg',
                'channel_id': channel_id
            }
            videos.append(video)
        return videos


class RealTimeDataCollector:
    """
    Real-time data collector that streams data from social media APIs
    """

    def __init__(self, config: AppConfig = None):
        if config is None:
            # Load from config file if not provided
            config = AppConfig.load_from_file()

        # Initialize API collectors with configuration
        self.twitter_collector = TwitterAPIDataCollector(config.twitter)
        self.youtube_collector = YouTubeAPIDataCollector(config.youtube)
        self.storage = DataStorage()

        # Threading components
        self.running = False
        self.twitter_thread = None
        self.youtube_thread = None

    def start_streaming(self):
        """Start real-time data collection from APIs"""
        self.running = True

        # Start Twitter streaming in a separate thread
        self.twitter_thread = threading.Thread(target=self._twitter_stream_worker, daemon=True)
        self.twitter_thread.start()

        # Start YouTube streaming in a separate thread
        self.youtube_thread = threading.Thread(target=self._youtube_stream_worker, daemon=True)
        self.youtube_thread.start()

        print("Real-time data collection started...")

    def stop_streaming(self):
        """Stop real-time data collection"""
        self.running = False

        print("Real-time data collection stopped.")

    def _twitter_stream_worker(self):
        """Worker function for Twitter streaming"""
        # Define keywords to track (you can customize this)
        tracked_keywords = ["technology", "python", "socialmedia", "dataanalytics"]

        while self.running:
            try:
                # Search for tweets with tracked keywords
                for keyword in tracked_keywords:
                    try:
                        tweets = self.twitter_collector.search_tweets(keyword, count=5)

                        for tweet in tweets:
                            # Store the tweet
                            self.storage.store_realtime_post({
                                'platform': 'Twitter',
                                'post_data': tweet
                            })

                            # Process the tweet for real-time analysis
                            self._process_realtime_tweet(tweet)

                        # Be respectful to the API - add delay
                        time.sleep(10)  # Increased delay to avoid rate limits
                    except Exception as e:
                        print(f"Rate limit or error for Twitter keyword '{keyword}': {e}")
                        # Wait longer if we hit a rate limit
                        time.sleep(900)  # Wait 15 minutes before trying again

            except Exception as e:
                print(f"Error in Twitter streaming: {e}")

            # Wait before next iteration
            time.sleep(600)  # Increased to 10 minutes before next search cycle

    def _youtube_stream_worker(self):
        """Worker function for YouTube streaming"""
        # Define topics to monitor (you can customize this)
        tracked_topics = ["technology", "python", "socialmedia", "dataanalytics"]

        while self.running:
            try:
                # Get videos with tracked topics
                for topic in tracked_topics:
                    try:
                        videos = self.youtube_collector.search_videos(topic, count=2)  # Reduced count

                        for video in videos:
                            # Store the video
                            self.storage.store_realtime_post({
                                'platform': 'YouTube',
                                'post_data': video
                            })

                            # Process the video for real-time analysis
                            self._process_realtime_video(video)

                        # Be respectful to the API - add delay
                        time.sleep(15)  # Increased delay to avoid rate limits
                    except Exception as e:
                        print(f"Rate limit or error for YouTube topic '{topic}': {e}")
                        # Wait longer if we hit a rate limit
                        time.sleep(900)  # Wait 15 minutes before trying again

            except Exception as e:
                print(f"Error in YouTube streaming: {e}")

            # Wait before next iteration
            time.sleep(1200)  # Increased to 20 minutes before next search cycle

    def _process_realtime_tweet(self, tweet_data):
        """Process a real-time tweet for analysis"""
        # Calculate engagement score
        engagement_score = (
            tweet_data.get('likes', 0) +
            (tweet_data.get('retweets', 0) * 2) +
            (tweet_data.get('replies', 0) * 1.5) +
            (tweet_data.get('quotes', 0) * 1.5)
        )

        # Check if engagement is significant
        if engagement_score > 100:  # Threshold for significant engagement
            print(f"High engagement tweet detected: {engagement_score} - {tweet_data.get('text', '')[:50]}...")

        # Extract hashtags for trend analysis
        text = tweet_data.get('text', '')
        hashtags = [tag for tag in text.split() if tag.startswith('#')]

        if hashtags:
            print(f"Hashtags detected: {hashtags}")

    def _process_realtime_video(self, video_data):
        """Process a real-time YouTube video for analysis"""
        # Calculate engagement score for YouTube
        engagement_score = (
            video_data.get('like_count', 0) +
            (video_data.get('comment_count', 0) * 0.8) +
            (video_data.get('view_count', 0) * 0.01)  # Views contribute less to engagement
        )

        # Check if engagement is significant
        if engagement_score > 500:  # Threshold for significant engagement
            print(f"High engagement YouTube video detected: {engagement_score} - {video_data.get('title', '')[:50]}...")

        # Print video details
        print(f"YouTube video from {video_data.get('channel_id', 'unknown')}: {video_data.get('title', '')[:50]}...")



class PersonalViewingTracker:
    """
    Tracks personal viewing activity for recommendations
    """

    def __init__(self, storage):
        self.storage = storage

    def track_viewing_activity(self, user_id: str, platform: str, content_id: str,
                              watch_duration: int = 0, engagement_type: str = 'view',
                              content_title: str = '', content_url: str = '', tags: list = None):
        """
        Track personal viewing activity
        """
        viewing_data = {
            'platform': platform.lower(),
            'content_id': content_id,
            'user_id': user_id,
            'watch_duration': watch_duration,
            'engagement_type': engagement_type,
            'content_title': content_title,
            'content_url': content_url,
            'tags': tags or []
        }

        # Store the viewing activity
        self.storage.store_personal_viewing(viewing_data)

        # Update user preferences based on content tags
        for tag in viewing_data['tags']:
            tag_clean = tag.lstrip('#').lower()
            self.storage.update_user_preference(user_id, 'hashtag', tag_clean)

        return viewing_data


def collect_platform_data(platform: str, identifier: str, count: int = 10) -> Dict:
    """Collect data from specified platform (original batch collection)"""
    if platform.lower() == 'twitter':
        collector = TwitterDataCollector()
        posts = collector.get_posts_data(identifier, count)
        user_metrics = collector.get_user_metrics(identifier)

        return {
            'platform': 'Twitter',
            'identifier': identifier,
            'posts': posts,
            'metrics': user_metrics
        }

    elif platform.lower() == 'youtube':
        collector = YouTubeDataCollector()
        videos = collector.get_video_data(identifier, count)
        channel_metrics = collector.get_channel_metrics(identifier)

        return {
            'platform': 'YouTube',
            'identifier': identifier,
            'posts': videos,  # Using 'posts' key to maintain compatibility
            'metrics': channel_metrics
        }

    elif platform.lower() == 'instagram':
        from instagram_collector import InstagramDataCollector
        collector = InstagramDataCollector()
        posts = collector.get_posts_data(identifier, count)
        user_metrics = collector.get_user_metrics(identifier)

        return {
            'platform': 'Instagram',
            'identifier': identifier,
            'posts': posts,
            'metrics': user_metrics
        }

    else:
        raise ValueError(f"Unsupported platform: {platform}")