from datetime import datetime, timedelta
from typing import Dict, List
import statistics
from collections import Counter
import threading
import time
import numpy as np


class SocialMediaAnalyzer:
    """
    Analyzes social media data to extract insights about audience demographics and engagement
    """

    def __init__(self):
        self.trend_detector = TrendDetector()
        self.alert_thresholds = {
            'twitter': 100,  # Engagement threshold for Twitter
            'youtube': 500,   # Engagement threshold for YouTube
        }

    def analyze_engagement(self, platform_data: Dict) -> Dict:
        """Analyze engagement metrics for a platform"""
        if not platform_data or 'posts' not in platform_data:
            return {}

        posts = platform_data['posts']
        platform = platform_data['platform'].lower()

        # Calculate engagement metrics based on platform
        if platform == 'twitter':
            likes = [post.get('likes', 0) for post in posts]
            retweets = [post.get('retweets', 0) for post in posts]
            replies = [post.get('replies', 0) for post in posts]

            engagement_scores = [
                post.get('likes', 0) + (post.get('retweets', 0) * 2) + post.get('replies', 0)
                for post in posts
            ]

        elif platform == 'youtube':
            views = [post.get('views', 0) for post in posts]
            likes = [post.get('likes', 0) for post in posts]
            comments = [post.get('comments', 0) for post in posts]

            engagement_scores = [
                (post.get('views', 0) * 0.01) + post.get('likes', 0) + (post.get('comments', 0) * 1.5)
                for post in posts
            ]


        # Calculate additional sophisticated metrics
        if engagement_scores:
            # Calculate engagement rate metrics
            total_engagement = sum(engagement_scores)
            engagement_rate = total_engagement / len(engagement_scores) if len(engagement_scores) > 0 else 0

            # Calculate engagement velocity (change over time)
            engagement_velocity = self._calculate_engagement_velocity(posts, platform)

            # Calculate engagement distribution metrics
            engagement_percentiles = self._calculate_percentiles(engagement_scores)

            # Calculate volatility (how much engagement varies)
            volatility = self._calculate_volatility(engagement_scores)

            # Calculate growth rate
            growth_rate = self._calculate_growth_rate(engagement_scores)
        else:
            engagement_rate = 0
            engagement_velocity = 0
            engagement_percentiles = {}
            volatility = 0
            growth_rate = 0

        # Calculate statistics
        analysis = {
            'total_posts': len(posts),
            'avg_engagement': round(statistics.mean(engagement_scores), 2) if engagement_scores else 0,
            'median_engagement': statistics.median(engagement_scores) if engagement_scores else 0,
            'max_engagement': max(engagement_scores) if engagement_scores else 0,
            'min_engagement': min(engagement_scores) if engagement_scores else 0,
            'std_deviation': round(statistics.stdev(engagement_scores), 2) if len(engagement_scores) > 1 else 0,
            'engagement_rate': round(engagement_rate, 2),
            'engagement_velocity': round(engagement_velocity, 2),
            'engagement_percentiles': engagement_percentiles,
            'volatility': round(volatility, 2),
            'growth_rate': round(growth_rate, 2)
        }

        if platform == 'twitter':
            analysis.update({
                'avg_likes': round(statistics.mean(likes), 2) if likes else 0,
                'avg_retweets': round(statistics.mean(retweets), 2) if retweets else 0,
                'avg_replies': round(statistics.mean(replies), 2) if replies else 0
            })
        elif platform == 'youtube':
            analysis.update({
                'avg_views': round(statistics.mean(views), 2) if views else 0,
                'avg_likes': round(statistics.mean(likes), 2) if likes else 0,
                'avg_comments': round(statistics.mean(comments), 2) if comments else 0
            })

        return analysis

    def analyze_personal_viewing_patterns(self, viewing_history: List[Dict]) -> Dict:
        """Analyze personal viewing patterns to identify preferences and habits"""
        if not viewing_history:
            return {}

        # Analyze platform preferences
        platform_counts = {}
        total_watch_time = 0
        content_count = len(viewing_history)

        for view in viewing_history:
            platform = view.get('platform', 'unknown').lower()
            watch_duration = view.get('watch_duration', 0)

            platform_counts[platform] = platform_counts.get(platform, 0) + 1
            total_watch_time += watch_duration

        # Analyze engagement types
        engagement_counts = {}
        for view in viewing_history:
            engagement_type = view.get('engagement_type', 'view')
            engagement_counts[engagement_type] = engagement_counts.get(engagement_type, 0) + 1

        # Analyze time patterns
        time_of_day_counts = {}
        for view in viewing_history:
            try:
                timestamp = view.get('timestamp', '')
                if timestamp:
                    from datetime import datetime
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    hour = dt.hour
                    time_of_day_counts[hour] = time_of_day_counts.get(hour, 0) + 1
            except ValueError:
                continue

        # Analyze tags/hashtags preferences
        tag_counts = {}
        for view in viewing_history:
            tags_str = view.get('tags', '')
            if tags_str:
                try:
                    import json
                    tags = json.loads(tags_str) if isinstance(tags_str, str) else tags_str
                    for tag in tags:
                        tag_clean = tag.lstrip('#').lower()
                        tag_counts[tag_clean] = tag_counts.get(tag_clean, 0) + 1
                except:
                    pass

        analysis = {
            'total_content_viewed': content_count,
            'total_watch_time': total_watch_time,
            'average_watch_time': total_watch_time / content_count if content_count > 0 else 0,
            'platform_preferences': platform_counts,
            'engagement_preferences': engagement_counts,
            'time_of_day_preferences': time_of_day_counts,
            'preferred_tags': dict(sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:10]),
            'favorite_platform': max(platform_counts, key=platform_counts.get) if platform_counts else None
        }

        return analysis

    def analyze_audience_demographics(self, platform_data: Dict) -> Dict:
        """Analyze audience demographics based on available data"""
        if not platform_data or 'posts' not in platform_data:
            return {}

        posts = platform_data['posts']
        platform = platform_data['platform'].lower()

        # Analyze location data if available
        locations = [post.get('location') for post in posts if post.get('location')]
        location_counts = Counter(locations)

        # Analyze posting times to infer active hours
        timestamps = [post.get('timestamp') for post in posts if post.get('timestamp')]
        hours_active = []

        for ts in timestamps:
            try:
                dt = datetime.fromisoformat(ts.replace('Z', '+00:00'))
                hours_active.append(dt.hour)
            except ValueError:
                continue

        hour_counts = Counter(hours_active)

        # Analyze hashtags for topic trends
        all_hashtags = []
        for post in posts:
            if 'hashtags' in post and post['hashtags']:
                all_hashtags.extend(post['hashtags'])

        hashtag_counts = Counter(all_hashtags)

        demographics = {
            'top_locations': dict(location_counts.most_common(5)),
            'peak_activity_hours': dict(hour_counts.most_common(5)),
            'top_hashtags': dict(hashtag_counts.most_common(10)),
            'total_unique_locations': len(location_counts),
            'most_active_hour': hour_counts.most_common(1)[0][0] if hour_counts else None
        }

        return demographics

    def _calculate_engagement_velocity(self, posts: List[Dict], platform: str) -> float:
        """Calculate the rate of change in engagement over time"""
        if len(posts) < 2:
            return 0

        # Sort posts by timestamp
        sorted_posts = sorted(posts, key=lambda x: x.get('timestamp', ''))

        # Calculate engagement for each post
        engagements = []
        timestamps = []

        for post in sorted_posts:
            if platform == 'twitter':
                engagement = post.get('likes', 0) + (post.get('retweets', 0) * 2) + post.get('replies', 0)
            elif platform == 'youtube':
                engagement = (post.get('views', 0) * 0.01) + post.get('likes', 0) + (post.get('comments', 0) * 1.5)
            else:
                engagement = 0

            engagements.append(engagement)

            # Convert timestamp to a numeric value for calculation
            try:
                ts = datetime.fromisoformat(post.get('timestamp', '').replace('Z', '+00:00'))
                timestamps.append(ts.timestamp())
            except ValueError:
                timestamps.append(0)

        # Calculate velocity as the slope of engagement over time
        if len(timestamps) > 1 and timestamps[-1] != timestamps[0]:
            time_diff = timestamps[-1] - timestamps[0]
            engagement_diff = engagements[-1] - engagements[0]
            velocity = engagement_diff / time_diff if time_diff != 0 else 0
        else:
            velocity = 0

        return velocity

    def _calculate_percentiles(self, data: List[float]) -> Dict[str, float]:
        """Calculate percentiles for engagement data"""
        if len(data) < 2:
            return {}

        sorted_data = sorted(data)
        n = len(sorted_data)

        percentiles = {
            'p25': sorted_data[int(0.25 * n)],
            'p50': sorted_data[int(0.50 * n)],  # median
            'p75': sorted_data[int(0.75 * n)],
            'p90': sorted_data[int(0.90 * n)],
            'p95': sorted_data[int(0.95 * n)],
            'p99': sorted_data[int(0.99 * n)]
        }

        return percentiles

    def _calculate_volatility(self, data: List[float]) -> float:
        """Calculate volatility as the coefficient of variation"""
        if len(data) < 2 or statistics.mean(data) == 0:
            return 0

        std_dev = statistics.stdev(data)
        mean_val = statistics.mean(data)

        # Coefficient of variation
        cv = std_dev / abs(mean_val) if mean_val != 0 else 0
        return cv

    def _calculate_growth_rate(self, data: List[float]) -> float:
        """Calculate growth rate as percentage change from first to last value"""
        if len(data) < 2:
            return 0

        first_val = data[0]
        last_val = data[-1]

        if first_val == 0:
            return float('inf') if last_val > 0 else 0

        growth_rate = ((last_val - first_val) / abs(first_val)) * 100
        return growth_rate

    def compare_platform_performance(self, twitter_data: Dict, youtube_data: Dict) -> Dict:
        """Compare performance between Twitter and YouTube"""
        comparison = {}

        # Analyze engagement for both platforms
        tw_engagement = self.analyze_engagement(twitter_data) if twitter_data else {}
        yt_engagement = self.analyze_engagement(youtube_data) if youtube_data else {}

        comparison['twitter_engagement'] = tw_engagement
        comparison['youtube_engagement'] = yt_engagement

        # Calculate ratios and differences
        if tw_engagement and yt_engagement:
            comparison['engagement_ratio'] = {
                'twitter_to_youtube': (
                    tw_engagement.get('avg_engagement', 0) / yt_engagement.get('avg_engagement', 1)
                    if yt_engagement.get('avg_engagement', 0) != 0 else float('inf')
                ),
                'youtube_to_twitter': (
                    yt_engagement.get('avg_engagement', 0) / tw_engagement.get('avg_engagement', 1)
                    if tw_engagement.get('avg_engagement', 0) != 0 else float('inf')
                )
            }

        return comparison

    def generate_insights(self, twitter_data: Dict, youtube_data: Dict) -> List[str]:
        """Generate actionable insights based on the analysis"""
        insights = []

        # Twitter insights
        if twitter_data:
            tw_engagement = self.analyze_engagement(twitter_data)
            tw_demographics = self.analyze_audience_demographics(twitter_data)

            if tw_engagement:
                avg_engagement = tw_engagement.get('avg_engagement', 0)
                if avg_engagement > 100:
                    insights.append(f"Twitter shows high engagement (avg: {avg_engagement}). Keep creating similar content.")
                elif avg_engagement < 50:
                    insights.append(f"Twitter engagement is low (avg: {avg_engagement}). Consider changing content strategy.")

                top_locations = tw_demographics.get('top_locations', {})
                if top_locations:
                    top_location = next(iter(top_locations))
                    insights.append(f"Most of your Twitter audience is from {top_location}. Target content to this region.")

                peak_hour = tw_demographics.get('most_active_hour')
                if peak_hour is not None:
                    insights.append(f"Your Twitter audience is most active at {peak_hour}:00. Post during this time for maximum reach.")

        # YouTube insights
        if youtube_data:
            yt_engagement = self.analyze_engagement(youtube_data)
            yt_demographics = self.analyze_audience_demographics(youtube_data)

            if yt_engagement:
                avg_engagement = yt_engagement.get('avg_engagement', 0)
                if avg_engagement > 500:
                    insights.append(f"YouTube shows high engagement (avg: {avg_engagement}). Keep creating similar content.")
                elif avg_engagement < 100:
                    insights.append(f"YouTube engagement is low (avg: {avg_engagement}). Consider changing content strategy.")

                top_locations = yt_demographics.get('top_locations', {})
                if top_locations:
                    top_location = next(iter(top_locations))
                    insights.append(f"Most of your YouTube audience is from {top_location}. Tailor content to this community.")

        # Cross-platform insights
        if twitter_data and youtube_data:
            comparison = self.compare_platform_performance(twitter_data, youtube_data)
            engagement_ratio = comparison.get('engagement_ratio', {})

            tw_to_yt = engagement_ratio.get('twitter_to_youtube', 0)
            if tw_to_yt > 2:
                insights.append("Twitter performs significantly better than YouTube. Focus more resources on Twitter.")
            elif tw_to_yt < 0.5:
                insights.append("YouTube performs significantly better than Twitter. Focus more resources on YouTube.")

        # Content insights
        if twitter_data:
            tw_demographics = self.analyze_audience_demographics(twitter_data)
            top_hashtags = tw_demographics.get('top_hashtags', {})

            if top_hashtags:
                top_hashtag = next(iter(top_hashtags))
                insights.append(f"Your most popular hashtag is {top_hashtag}. Use this and similar hashtags more often.")

        return insights

    def get_peak_times(self, platform_data: Dict) -> Dict:
        """Identify peak activity times for optimal posting"""
        if not platform_data or 'posts' not in platform_data:
            return {}

        posts = platform_data['posts']
        timestamps = [post.get('timestamp') for post in posts if post.get('timestamp')]

        hours = []
        days_of_week = []

        for ts in timestamps:
            try:
                dt = datetime.fromisoformat(ts.replace('Z', '+00:00'))
                hours.append(dt.hour)
                days_of_week.append(dt.weekday())  # Monday is 0, Sunday is 6
            except ValueError:
                continue

        hour_counts = Counter(hours)
        day_counts = Counter(days_of_week)

        # Convert day numbers to names
        day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        day_name_counts = {day_names[day]: count for day, count in day_counts.items()}

        return {
            'peak_hours': dict(hour_counts.most_common(5)),
            'peak_days': day_name_counts,
            'best_hour_for_posting': hour_counts.most_common(1)[0][0] if hour_counts else None,
            'best_day_for_posting': day_names[day_counts.most_common(1)[0][0]] if day_counts else None
        }

    def _analyze_sentiment(self, text: str) -> float:
        """
        Analyze sentiment of text content.
        Returns a score between -1 (very negative) and 1 (very positive).
        This is a simplified implementation; in a real application,
        you would use a library like TextBlob or VADER.
        """
        if not text:
            return 0.0

        # Simplified sentiment analysis based on common positive/negative words
        positive_words = [
            'good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic',
            'love', 'like', 'awesome', 'brilliant', 'outstanding', 'perfect',
            'happy', 'joy', 'pleased', 'satisfied', 'delighted', 'thrilled',
            'positive', 'incredible', 'superb', 'marvelous', 'fabulous'
        ]

        negative_words = [
            'bad', 'terrible', 'awful', 'horrible', 'hate', 'dislike',
            'disappointing', 'sad', 'angry', 'frustrated', 'annoyed',
            'negative', 'worst', 'pathetic', 'useless', 'horrific',
            'disgusting', 'atrocious', 'dreadful', 'appalling', 'abysmal'
        ]

        # Convert to lowercase and split into words
        words = text.lower().split()

        positive_count = sum(1 for word in words if word in positive_words)
        negative_count = sum(1 for word in words if word in negative_words)

        # Calculate sentiment score
        total_sentiment_words = positive_count + negative_count
        if total_sentiment_words == 0:
            return 0.0

        sentiment_score = (positive_count - negative_count) / total_sentiment_words
        # Clamp between -1 and 1
        sentiment_score = max(-1.0, min(1.0, sentiment_score))

        return sentiment_score

    def analyze_realtime_post(self, post_data: Dict) -> Dict:
        """Analyze a single real-time post and return insights"""
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

        # Check if engagement exceeds threshold
        is_significant = engagement_score > self.alert_thresholds.get(platform, 100)

        # Extract hashtags if available
        hashtags = []
        if platform == 'twitter' and 'text' in post:
            text = post['text']
            hashtags = [tag for tag in text.split() if tag.startswith('#')]
        elif platform == 'youtube' and 'tags' in post:
            tags = post['tags']
            hashtags = [tag for tag in tags if tag.startswith('#')]
        elif 'hashtags' in post:
            hashtags = post['hashtags']

        # Update trend detector
        for hashtag in hashtags:
            self.trend_detector.add_hashtag(hashtag)

        # Perform sentiment analysis if possible
        content = post.get('text', post.get('title', post.get('caption', '')))
        sentiment_score = self._analyze_sentiment(content)

        return {
            'engagement_score': engagement_score,
            'is_significant': is_significant,
            'hashtags': hashtags,
            'trending_hashtags': self.trend_detector.get_trending_hashtags(),
            'sentiment_score': sentiment_score
        }


class TrendDetector:
    """
    Detects trending topics in real-time
    """
    def __init__(self, time_window_minutes=10):
        self.time_window = time_window_minutes * 60  # Convert to seconds
        self.hashtag_counts = Counter()  # Store counts of hashtags
        self.hashtag_timestamps = {}  # Store timestamps for each hashtag
        self.trend_threshold = 5  # Minimum mentions to be considered trending
        self.lock = threading.Lock()  # Thread safety

    def add_hashtag(self, hashtag, timestamp=None):
        """Add a hashtag and its timestamp to track trends"""
        if timestamp is None:
            timestamp = time.time()

        with self.lock:
            # Normalize hashtag (lowercase, remove #)
            normalized_hashtag = hashtag.lower().lstrip('#')

            # Update count
            self.hashtag_counts[normalized_hashtag] += 1

            # Store timestamp
            if normalized_hashtag not in self.hashtag_timestamps:
                self.hashtag_timestamps[normalized_hashtag] = []
            self.hashtag_timestamps[normalized_hashtag].append(timestamp)

            # Clean up old entries outside the time window
            self._cleanup_old_entries(normalized_hashtag)

    def _cleanup_old_entries(self, hashtag):
        """Remove entries older than the time window"""
        current_time = time.time()
        valid_timestamps = [
            ts for ts in self.hashtag_timestamps[hashtag]
            if current_time - ts <= self.time_window
        ]

        # Update counts based on valid timestamps only
        self.hashtag_timestamps[hashtag] = valid_timestamps
        self.hashtag_counts[hashtag] = len(valid_timestamps)

    def get_trending_hashtags(self, limit=10):
        """Return currently trending hashtags"""
        with self.lock:
            # Get hashtags that exceed the trend threshold
            trending = [
                {'hashtag': hashtag, 'mention_count': count}
                for hashtag, count in self.hashtag_counts.items()
                if count >= self.trend_threshold
            ]

            # Sort by mention count
            trending.sort(key=lambda x: x['mention_count'], reverse=True)

            return trending[:limit]  # Return top N trending hashtags

    def get_hashtag_frequency(self, hashtag):
        """Get the frequency of a specific hashtag in the time window"""
        normalized_hashtag = hashtag.lower().lstrip('#')
        return self.hashtag_counts.get(normalized_hashtag, 0)


class RealTimeAnalyzer:
    """
    Real-time analyzer that processes data as it comes in
    """
    def __init__(self):
        self.analyzer = SocialMediaAnalyzer()
        self.alert_callbacks = []

    def add_alert_callback(self, callback):
        """Add a callback function to be called when significant events occur"""
        self.alert_callbacks.append(callback)

    def process_realtime_post(self, post_data):
        """Process a single real-time post"""
        # Analyze the post
        analysis = self.analyzer.analyze_realtime_post(post_data)

        # If the post is significant, trigger alerts
        if analysis.get('is_significant', False):
            for callback in self.alert_callbacks:
                try:
                    callback(post_data, analysis)
                except Exception as e:
                    print(f"Error in alert callback: {e}")

        return analysis