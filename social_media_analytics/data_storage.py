import json
import sqlite3
from datetime import datetime
from typing import Dict, List
import os


class DataStorage:
    """
    Handles storing collected social media data
    Uses SQLite for simplicity, but could be extended to other databases
    """
    
    def __init__(self, db_path: str = "social_media_data.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Table for storing post data
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                platform TEXT NOT NULL,
                post_id TEXT UNIQUE NOT NULL,
                identifier TEXT NOT NULL,
                content TEXT,
                timestamp TEXT,
                likes INTEGER DEFAULT 0,
                shares INTEGER DEFAULT 0,
                comments INTEGER DEFAULT 0,
                engagement_score REAL DEFAULT 0.0,
                hashtags TEXT,
                location TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Table for storing metrics
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                platform TEXT NOT NULL,
                identifier TEXT NOT NULL,
                metric_type TEXT NOT NULL,
                value REAL,
                unit TEXT,
                recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def store_posts(self, platform_data: Dict):
        """Store collected posts in the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        platform = platform_data['platform']
        identifier = platform_data['identifier']
        
        for post in platform_data['posts']:
            # Calculate engagement score based on likes, shares, comments
            engagement_score = 0
            if platform.lower() == 'twitter':
                engagement_score = post.get('likes', 0) + (post.get('retweets', 0) * 2) + post.get('replies', 0)
            elif platform.lower() == 'reddit':
                engagement_score = post.get('upvotes', 0) + post.get('comments', 0)
            
            # Prepare hashtags as JSON string
            hashtags_str = json.dumps(post.get('hashtags', [])) if post.get('hashtags') else None
            
            try:
                cursor.execute('''
                    INSERT OR REPLACE INTO posts 
                    (platform, post_id, identifier, content, timestamp, 
                     likes, shares, comments, engagement_score, hashtags, location)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    platform,
                    post['post_id'],
                    identifier,
                    post.get('text') or post.get('title'),
                    post['timestamp'],
                    post.get('likes', 0),
                    post.get('retweets', 0) if platform.lower() == 'twitter' else post.get('upvotes', 0),
                    post.get('replies', 0) if platform.lower() == 'twitter' else post.get('comments', 0),
                    engagement_score,
                    hashtags_str,
                    post.get('location')
                ))
            except sqlite3.IntegrityError:
                # Handle duplicate post_id
                continue
        
        conn.commit()
        conn.close()
    
    def store_metrics(self, platform_data: Dict):
        """Store metrics in the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        platform = platform_data['platform']
        identifier = platform_data['identifier']
        metrics = platform_data['metrics']
        
        for metric_name, metric_value in metrics.items():
            # Determine unit based on metric name
            unit_map = {
                'followers': 'count',
                'following': 'count',
                'tweets_count': 'count',
                'account_age_days': 'days',
                'engagement_rate': 'percentage',
                'members': 'count',
                'active_users': 'count',
                'posts_per_day': 'count',
                'avg_comments_per_post': 'count',
                'community_age_days': 'days'
            }
            
            unit = unit_map.get(metric_name, 'count')
            
            cursor.execute('''
                INSERT INTO metrics 
                (platform, identifier, metric_type, value, unit)
                VALUES (?, ?, ?, ?, ?)
            ''', (platform, identifier, metric_name, metric_value, unit))
        
        conn.commit()
        conn.close()
    
    def get_posts_by_platform(self, platform: str) -> List[Dict]:
        """Retrieve all posts for a specific platform"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM posts WHERE platform = ?', (platform,))
        rows = cursor.fetchall()
        
        columns = [description[0] for description in cursor.description]
        posts = [dict(zip(columns, row)) for row in rows]
        
        conn.close()
        return posts
    
    def get_metrics_by_platform(self, platform: str) -> List[Dict]:
        """Retrieve all metrics for a specific platform"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM metrics WHERE platform = ?', (platform,))
        rows = cursor.fetchall()
        
        columns = [description[0] for description in cursor.description]
        metrics = [dict(zip(columns, row)) for row in rows]
        
        conn.close()
        return metrics
    
    def get_recent_posts(self, limit: int = 20) -> List[Dict]:
        """Get most recent posts across all platforms"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM posts 
            ORDER BY created_at DESC 
            LIMIT ?
        ''', (limit,))
        rows = cursor.fetchall()
        
        columns = [description[0] for description in cursor.description]
        posts = [dict(zip(columns, row)) for row in rows]
        
        conn.close()
        return posts