import json
import sqlite3
from datetime import datetime
from typing import Dict, List
import os
import threading


class DataStorage:
    """
    Handles storing collected social media data
    Uses SQLite for simplicity, but could be extended to other databases
    """

    def __init__(self, db_path: str = "social_media_data.db"):
        self.db_path = db_path
        self.lock = threading.Lock()  # For thread safety
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

        # Table for storing real-time posts
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS realtime_posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                platform TEXT NOT NULL,
                post_id TEXT UNIQUE NOT NULL,
                content TEXT,
                timestamp TEXT,
                engagement_score REAL DEFAULT 0.0,
                hashtags TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Table for storing personal viewing activity
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS personal_viewing (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                platform TEXT NOT NULL,
                content_id TEXT NOT NULL,
                user_id TEXT DEFAULT 'default_user',
                watch_duration INTEGER DEFAULT 0,  -- in seconds
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                engagement_type TEXT DEFAULT 'view',  -- view, like, comment, share
                content_title TEXT,
                content_url TEXT,
                tags TEXT
            )
        ''')

        # Table for storing user preferences and interests
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_preferences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT DEFAULT 'default_user',
                preference_type TEXT NOT NULL,  -- hashtag, topic, category
                preference_value TEXT NOT NULL,
                frequency INTEGER DEFAULT 1,
                last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Create indexes separately
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_platform_timestamp ON realtime_posts (platform, created_at)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_engagement_score ON realtime_posts (engagement_score)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_personal_viewing_user ON personal_viewing (user_id, timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_personal_viewing_content ON personal_viewing (content_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_preferences_user ON user_preferences (user_id, preference_type)')

        conn.commit()
        conn.close()

    def store_personal_viewing(self, viewing_data: Dict):
        """Store personal viewing activity in the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        platform = viewing_data.get('platform', '').lower()
        content_id = viewing_data.get('content_id', '')
        user_id = viewing_data.get('user_id', 'default_user')
        watch_duration = viewing_data.get('watch_duration', 0)
        engagement_type = viewing_data.get('engagement_type', 'view')
        content_title = viewing_data.get('content_title', '')
        content_url = viewing_data.get('content_url', '')
        tags = viewing_data.get('tags', [])

        # Convert tags to JSON string
        tags_str = json.dumps(tags) if tags else None

        try:
            cursor.execute('''
                INSERT INTO personal_viewing
                (platform, content_id, user_id, watch_duration, engagement_type, content_title, content_url, tags)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                platform,
                content_id,
                user_id,
                watch_duration,
                engagement_type,
                content_title,
                content_url,
                tags_str
            ))

            conn.commit()
        except sqlite3.Error as e:
            print(f"Database error while storing personal viewing data: {e}")
        finally:
            conn.close()

    def get_personal_viewing_history(self, user_id: str = 'default_user', limit: int = 50) -> List[Dict]:
        """Get personal viewing history for a user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM personal_viewing
            WHERE user_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (user_id, limit))
        rows = cursor.fetchall()

        columns = [description[0] for description in cursor.description]
        viewing_history = [dict(zip(columns, row)) for row in rows]

        conn.close()
        return viewing_history

    def get_viewing_stats_24h(self, user_id: str = 'default_user') -> Dict:
        """Get viewing statistics for the last 24 hours"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT platform, COUNT(*) as count, SUM(watch_duration) as total_duration
            FROM personal_viewing
            WHERE user_id = ? AND timestamp >= datetime('now', '-1 day')
            GROUP BY platform
        ''', (user_id,))
        rows = cursor.fetchall()

        stats = {}
        for row in rows:
            platform, count, total_duration = row
            stats[platform] = {
                'content_count': count,
                'total_watch_duration': total_duration or 0
            }

        conn.close()
        return stats

    def update_user_preference(self, user_id: str, preference_type: str, preference_value: str):
        """Update user preferences based on viewing activity"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Check if preference already exists
        cursor.execute('''
            SELECT id, frequency FROM user_preferences
            WHERE user_id = ? AND preference_type = ? AND preference_value = ?
        ''', (user_id, preference_type, preference_value))
        result = cursor.fetchone()

        if result:
            # Update existing preference
            pref_id, frequency = result
            cursor.execute('''
                UPDATE user_preferences
                SET frequency = ?, last_used = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (frequency + 1, pref_id))
        else:
            # Insert new preference
            cursor.execute('''
                INSERT INTO user_preferences (user_id, preference_type, preference_value)
                VALUES (?, ?, ?)
            ''', (user_id, preference_type, preference_value))

        conn.commit()
        conn.close()

    def get_user_preferences(self, user_id: str = 'default_user', preference_type: str = None) -> List[Dict]:
        """Get user preferences, optionally filtered by type"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        if preference_type:
            cursor.execute('''
                SELECT * FROM user_preferences
                WHERE user_id = ? AND preference_type = ?
                ORDER BY frequency DESC
            ''', (user_id, preference_type))
        else:
            cursor.execute('''
                SELECT * FROM user_preferences
                WHERE user_id = ?
                ORDER BY frequency DESC
            ''', (user_id,))

        rows = cursor.fetchall()

        columns = [description[0] for description in cursor.description]
        preferences = [dict(zip(columns, row)) for row in rows]

        conn.close()
        return preferences

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
            elif platform.lower() == 'youtube':
                engagement_score = (post.get('views', 0) * 0.01) + post.get('likes', 0) + (post.get('comments', 0) * 1.5)

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

    def store_realtime_post(self, post_data: Dict):
        """Store a single real-time post in the database"""
        platform = post_data.get('platform', '').lower()
        post = post_data.get('post_data', {})

        # Calculate engagement score
        if platform == 'twitter':
            engagement_score = (
                post.get('likes', 0) +
                (post.get('retweets', 0) * 2) +
                (post.get('replies', 0) * 1.5) +
                (post.get('quotes', 0) * 1.5)
            )
        elif platform == 'youtube':
            engagement_score = (
                (post.get('view_count', 0) * 0.01) +
                (post.get('like_count', 0) * 1.0) +
                (post.get('comment_count', 0) * 1.5)
            )
        else:
            engagement_score = 0

        # Prepare hashtags as JSON string
        hashtags = []
        if platform == 'twitter' and 'text' in post:
            text = post['text']
            hashtags = [tag for tag in text.split() if tag.startswith('#')]
        elif platform == 'youtube' and 'tags' in post:
            tags = post['tags']
            hashtags = [tag for tag in tags if tag.startswith('#')]
        elif 'hashtags' in post:
            hashtags = post['hashtags']

        hashtags_str = json.dumps(hashtags) if hashtags else None

        # Use thread-safe database access
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            try:
                cursor.execute('''
                    INSERT OR REPLACE INTO realtime_posts
                    (platform, post_id, content, timestamp, engagement_score, hashtags)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    platform,
                    post.get('post_id', f'realtime_{datetime.now().timestamp()}'),
                    post.get('text') or post.get('title') or post.get('body', ''),
                    post.get('timestamp', datetime.now().isoformat()),
                    engagement_score,
                    hashtags_str
                ))

                conn.commit()
            except sqlite3.Error as e:
                print(f"Database error while storing real-time post: {e}")
            finally:
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

    def get_recent_realtime_posts(self, platform: str = None, limit: int = 50) -> List[Dict]:
        """Get most recent real-time posts"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        if platform:
            cursor.execute('''
                SELECT * FROM realtime_posts
                WHERE platform = ?
                ORDER BY created_at DESC
                LIMIT ?
            ''', (platform, limit))
        else:
            cursor.execute('''
                SELECT * FROM realtime_posts
                ORDER BY created_at DESC
                LIMIT ?
            ''', (limit,))

        rows = cursor.fetchall()

        columns = [description[0] for description in cursor.description]
        posts = [dict(zip(columns, row)) for row in rows]

        conn.close()
        return posts

    def get_high_engagement_posts(self, min_engagement: int = 100, limit: int = 20) -> List[Dict]:
        """Get posts with high engagement scores"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM realtime_posts
            WHERE engagement_score >= ?
            ORDER BY engagement_score DESC
            LIMIT ?
        ''', (min_engagement, limit))
        rows = cursor.fetchall()

        columns = [description[0] for description in cursor.description]
        posts = [dict(zip(columns, row)) for row in rows]

        conn.close()
        return posts

    def get_trending_hashtags(self, hours: int = 1, limit: int = 10) -> List[Dict]:
        """Get trending hashtags in the last N hours"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT hashtags, COUNT(*) as count
            FROM realtime_posts
            WHERE created_at >= datetime('now', '-{} hours')
            AND hashtags IS NOT NULL
            GROUP BY hashtags
            ORDER BY count DESC
            LIMIT ?
        '''.format(hours), (limit,))
        rows = cursor.fetchall()

        # Parse hashtags from JSON strings and count individual hashtags
        hashtag_counts = {}
        for row in rows:
            try:
                hashtags = json.loads(row[0]) if row[0] else []
                for hashtag in hashtags:
                    hashtag = hashtag.lower().strip()  # Normalize
                    hashtag_counts[hashtag] = hashtag_counts.get(hashtag, 0) + 1
            except json.JSONDecodeError:
                continue

        # Sort by count and return top hashtags
        sorted_hashtags = sorted(hashtag_counts.items(), key=lambda x: x[1], reverse=True)

        conn.close()
        return [{'hashtag': h, 'count': c} for h, c in sorted_hashtags[:limit]]