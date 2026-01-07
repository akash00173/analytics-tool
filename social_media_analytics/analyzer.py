from datetime import datetime, timedelta
from typing import Dict, List
import statistics
from collections import Counter


class SocialMediaAnalyzer:
    """
    Analyzes social media data to extract insights about audience demographics and engagement
    """
    
    def __init__(self):
        pass
    
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
            
        elif platform == 'reddit':
            upvotes = [post.get('upvotes', 0) for post in posts]
            downvotes = [post.get('downvotes', 0) for post in posts]
            comments = [post.get('comments', 0) for post in posts]
            
            engagement_scores = [
                post.get('upvotes', 0) + post.get('comments', 0)
                for post in posts
            ]
        
        # Calculate statistics
        analysis = {
            'total_posts': len(posts),
            'avg_engagement': round(statistics.mean(engagement_scores), 2) if engagement_scores else 0,
            'median_engagement': statistics.median(engagement_scores) if engagement_scores else 0,
            'max_engagement': max(engagement_scores) if engagement_scores else 0,
            'min_engagement': min(engagement_scores) if engagement_scores else 0,
            'std_deviation': round(statistics.stdev(engagement_scores), 2) if len(engagement_scores) > 1 else 0
        }
        
        if platform == 'twitter':
            analysis.update({
                'avg_likes': round(statistics.mean(likes), 2) if likes else 0,
                'avg_retweets': round(statistics.mean(retweets), 2) if retweets else 0,
                'avg_replies': round(statistics.mean(replies), 2) if replies else 0
            })
        elif platform == 'reddit':
            analysis.update({
                'avg_upvotes': round(statistics.mean(upvotes), 2) if upvotes else 0,
                'avg_comments': round(statistics.mean(comments), 2) if comments else 0
            })
        
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
    
    def compare_platform_performance(self, twitter_data: Dict, reddit_data: Dict) -> Dict:
        """Compare performance between Twitter and Reddit"""
        comparison = {}
        
        # Analyze engagement for both platforms
        tw_engagement = self.analyze_engagement(twitter_data) if twitter_data else {}
        rd_engagement = self.analyze_engagement(reddit_data) if reddit_data else {}
        
        comparison['twitter_engagement'] = tw_engagement
        comparison['reddit_engagement'] = rd_engagement
        
        # Calculate ratios and differences
        if tw_engagement and rd_engagement:
            comparison['engagement_ratio'] = {
                'twitter_to_reddit': (
                    tw_engagement.get('avg_engagement', 0) / rd_engagement.get('avg_engagement', 1)
                    if rd_engagement.get('avg_engagement', 0) != 0 else float('inf')
                ),
                'reddit_to_twitter': (
                    rd_engagement.get('avg_engagement', 0) / tw_engagement.get('avg_engagement', 1)
                    if tw_engagement.get('avg_engagement', 0) != 0 else float('inf')
                )
            }
        
        return comparison
    
    def generate_insights(self, twitter_data: Dict, reddit_data: Dict) -> List[str]:
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
        
        # Reddit insights
        if reddit_data:
            rd_engagement = self.analyze_engagement(reddit_data)
            rd_demographics = self.analyze_audience_demographics(reddit_data)
            
            if rd_engagement:
                avg_engagement = rd_engagement.get('avg_engagement', 0)
                if avg_engagement > 500:
                    insights.append(f"Reddit shows high engagement (avg: {avg_engagement}). Keep creating similar content.")
                elif avg_engagement < 100:
                    insights.append(f"Reddit engagement is low (avg: {avg_engagement}). Consider changing content strategy.")
                
                top_locations = rd_demographics.get('top_locations', {})
                if top_locations:
                    top_location = next(iter(top_locations))
                    insights.append(f"Most of your Reddit audience is from {top_location}. Tailor content to this community.")
        
        # Cross-platform insights
        if twitter_data and reddit_data:
            comparison = self.compare_platform_performance(twitter_data, reddit_data)
            engagement_ratio = comparison.get('engagement_ratio', {})
            
            tw_to_rd = engagement_ratio.get('twitter_to_reddit', 0)
            if tw_to_rd > 2:
                insights.append("Twitter performs significantly better than Reddit. Focus more resources on Twitter.")
            elif tw_to_rd < 0.5:
                insights.append("Reddit performs significantly better than Twitter. Focus more resources on Reddit.")
        
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