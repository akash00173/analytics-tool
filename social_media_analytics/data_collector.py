import json
import random
from datetime import datetime, timedelta
from typing import Dict, List


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


class RedditDataCollector:
    """
    Simulates Reddit API data collection
    In a real implementation, this would connect to the Reddit API
    """
    
    def __init__(self):
        self.platform = "Reddit"
    
    def get_posts_data(self, subreddit: str, count: int = 10) -> List[Dict]:
        """Simulate getting post data from a subreddit"""
        posts = []
        for i in range(count):
            post = {
                'post_id': f'post_{random.randint(10000, 99999)}',
                'subreddit': subreddit,
                'title': f'Sample post {i+1} about {subreddit}',
                'body': f'This is the body content of post {i+1}',
                'timestamp': (datetime.now() - timedelta(days=random.randint(0, 30))).isoformat(),
                'upvotes': random.randint(0, 5000),
                'downvotes': random.randint(0, 500),
                'comments': random.randint(0, 1000),
                'awards': random.randint(0, 50),
                'author': f'user_{random.randint(1000, 9999)}'
            }
            posts.append(post)
        return posts
    
    def get_community_metrics(self, subreddit: str) -> Dict:
        """Simulate getting subreddit metrics"""
        return {
            'members': random.randint(1000, 1000000),
            'active_users': random.randint(100, 50000),
            'posts_per_day': random.randint(10, 1000),
            'avg_comments_per_post': random.randint(5, 50),
            'community_age_days': random.randint(100, 5000)
        }


def collect_platform_data(platform: str, identifier: str, count: int = 10) -> Dict:
    """Collect data from specified platform"""
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
    
    elif platform.lower() == 'reddit':
        collector = RedditDataCollector()
        posts = collector.get_posts_data(identifier, count)
        community_metrics = collector.get_community_metrics(identifier)
        
        return {
            'platform': 'Reddit',
            'identifier': identifier,
            'posts': posts,
            'metrics': community_metrics
        }
    
    else:
        raise ValueError(f"Unsupported platform: {platform}")