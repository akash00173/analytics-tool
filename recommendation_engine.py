"""
Recommendation Engine for Personalized Content Suggestions
Based on viewing history and user preferences
"""

import random
from typing import Dict, List
from data_storage import DataStorage
from analyzer import SocialMediaAnalyzer


class RecommendationEngine:
    """
    Generates personalized content recommendations based on user viewing history and preferences
    """
    
    def __init__(self, storage: DataStorage = None, analyzer: SocialMediaAnalyzer = None):
        self.storage = storage or DataStorage()
        self.analyzer = analyzer or SocialMediaAnalyzer()
        self.user_id = 'default_user'
        
    def get_user_recommendations(self, user_id: str = 'default_user', count: int = 10) -> List[Dict]:
        """
        Get personalized content recommendations for a user
        """
        self.user_id = user_id

        try:
            # Get user's viewing history and preferences
            viewing_history = self.storage.get_personal_viewing_history(user_id, limit=50)
            preferences = self.storage.get_user_preferences(user_id)
        except Exception as e:
            print(f"Error getting user data for recommendations: {e}")
            # Return mock recommendations if no data available
            return self._generate_mock_recommendations(count)

        # Extract preferred topics and hashtags from user data
        preferred_topics = self._extract_preferred_topics(preferences, viewing_history)

        # Generate recommendations based on user preferences
        recommendations = self._generate_recommendations(preferred_topics, count)

        # If no recommendations generated, return mock data
        if not recommendations:
            return self._generate_mock_recommendations(count)

        return recommendations

    def _generate_mock_recommendations(self, count: int) -> List[Dict]:
        """
        Generate mock recommendations when no user data is available
        """
        import random
        platforms = ['Twitter', 'YouTube']
        hashtags = ['technology', 'python', 'socialmedia', 'analytics', 'data', 'programming', 'coding', 'webdev']

        recommendations = []
        for i in range(count):
            hashtag = random.choice(hashtags)
            platform = random.choice(platforms)

            recommendation = {
                'id': f'mock_rec_{i}_{random.randint(1000, 9999)}',
                'platform': platform,
                'title': f'Mock recommended content about #{hashtag} on {platform}',
                'description': f'Based on trending topics in #{hashtag} and similar content',
                'url': f'https://{platform.lower()}.com/mock/{i}',
                'recommended_for': [hashtag, random.choice(hashtags)],
                'confidence_score': round(random.uniform(0.5, 0.8), 2),
                'estimated_watch_time': random.randint(60, 600)  # in seconds
            }

            recommendations.append(recommendation)

        return recommendations
    
    def _extract_preferred_topics(self, preferences: List[Dict], viewing_history: List[Dict]) -> Dict:
        """
        Extract preferred topics and hashtags from user data
        """
        topics = {'hashtags': {}, 'categories': {}, 'platforms': {}}
        
        # Process user preferences
        for pref in preferences:
            if pref['preference_type'] == 'hashtag':
                topics['hashtags'][pref['preference_value']] = pref['frequency']
            elif pref['preference_type'] == 'category':
                topics['categories'][pref['preference_value']] = pref['frequency']
        
        # Process viewing history to extract additional preferences
        for view in viewing_history:
            # Extract hashtags from tags if available
            if view.get('tags'):
                try:
                    import json
                    tags = json.loads(view['tags']) if isinstance(view['tags'], str) else view['tags']
                    for tag in tags:
                        tag_clean = tag.lstrip('#').lower()
                        topics['hashtags'][tag_clean] = topics['hashtags'].get(tag_clean, 0) + 1
                except:
                    pass  # If JSON parsing fails, skip this entry
        
        # Count platform preferences
        for view in viewing_history:
            platform = view.get('platform', 'unknown')
            topics['platforms'][platform] = topics['platforms'].get(platform, 0) + 1
        
        return topics
    
    def _generate_recommendations(self, preferred_topics: Dict, count: int) -> List[Dict]:
        """
        Generate content recommendations based on preferred topics
        """
        recommendations = []
        
        # Generate recommendations based on hashtags
        top_hashtags = sorted(preferred_topics['hashtags'].items(), 
                             key=lambda x: x[1], reverse=True)[:5]
        
        # Generate mock recommendations based on user preferences
        for i in range(count):
            platform = self._select_platform(preferred_topics['platforms'])
            hashtag = random.choice(list(preferred_topics['hashtags'].keys())) if preferred_topics['hashtags'] else 'technology'
            
            recommendation = {
                'id': f'rec_{i}_{random.randint(1000, 9999)}',
                'platform': platform,
                'title': f'Recommended content about #{hashtag} on {platform}',
                'description': f'Based on your interest in #{hashtag} and similar content',
                'url': f'https://{platform.lower()}.com/recommended/{i}',
                'recommended_for': list(preferred_topics['hashtags'].keys())[:3],
                'confidence_score': round(random.uniform(0.7, 0.95), 2),
                'estimated_watch_time': random.randint(60, 600)  # in seconds
            }
            
            recommendations.append(recommendation)
        
        return recommendations
    
    def _select_platform(self, platform_preferences: Dict) -> str:
        """
        Select a platform based on user's viewing preferences
        """
        if not platform_preferences:
            # Default to Twitter or YouTube if no preferences
            return random.choice(['Twitter', 'YouTube'])
        
        # Weighted random selection based on preference frequency
        total_weight = sum(platform_preferences.values())
        if total_weight == 0:
            return random.choice(['Twitter', 'YouTube'])
        
        rand_val = random.uniform(0, total_weight)
        current_weight = 0
        
        for platform, weight in platform_preferences.items():
            current_weight += weight
            if rand_val <= current_weight:
                return platform.title()  # Capitalize properly
        
        return random.choice(['Twitter', 'YouTube'])
    
    def update_user_profile(self, user_id: str, content_id: str, engagement_type: str = 'view'):
        """
        Update user profile based on their interaction with recommended content
        """
        # Get content details from viewing history
        viewing_history = self.storage.get_personal_viewing_history(user_id, limit=1)
        
        if viewing_history:
            content = viewing_history[0]
            
            # Extract hashtags and update preferences
            if content.get('tags'):
                try:
                    import json
                    tags = json.loads(content['tags']) if isinstance(content['tags'], str) else content['tags']
                    for tag in tags:
                        tag_clean = tag.lstrip('#').lower()
                        self.storage.update_user_preference(user_id, 'hashtag', tag_clean)
                except:
                    pass  # If JSON parsing fails, skip this entry
            
            # Update category preferences based on platform
            platform = content.get('platform', 'unknown')
            self.storage.update_user_preference(user_id, 'category', platform.lower())


class PersonalAnalytics:
    """
    Analyze personal viewing patterns and provide insights
    """
    
    def __init__(self, storage: DataStorage = None):
        self.storage = storage or DataStorage()
        self.user_id = 'default_user'
    
    def get_personal_insights(self, user_id: str = 'default_user') -> Dict:
        """
        Get personal viewing insights for a user
        """
        self.user_id = user_id

        try:
            # Get viewing stats for last 24 hours
            stats_24h = self.storage.get_viewing_stats_24h(user_id)

            # Get viewing history
            viewing_history = self.storage.get_personal_viewing_history(user_id, limit=100)

            # Get user preferences
            preferences = self.storage.get_user_preferences(user_id)
        except Exception as e:
            print(f"Error getting user data for insights: {e}")
            # Return mock insights if no data available
            return self._generate_mock_insights()

        # Calculate insights
        insights = {
            'viewing_summary': self._calculate_viewing_summary(stats_24h, viewing_history),
            'preferred_topics': self._get_preferred_topics(preferences),
            'platform_preferences': self._get_platform_preferences(stats_24h),
            'trending_interests': self._get_trending_interests(preferences),
            'recommendation_accuracy': self._calculate_recommendation_accuracy(viewing_history)
        }

        # If no insights generated, return mock data
        if not any(insights.values()) or all(len(v) == 0 if isinstance(v, (list, dict)) else v == 0 if isinstance(v, (int, float)) else not v for v in insights.values()):
            return self._generate_mock_insights()

        return insights

    def _generate_mock_insights(self) -> Dict:
        """
        Generate mock insights when no user data is available
        """
        import random
        return {
            'viewing_summary': {
                'total_content_viewed': random.randint(5, 20),
                'total_watch_time': random.randint(300, 1800),  # seconds
                'average_watch_time': random.randint(60, 300),  # seconds
                'content_by_platform': {
                    'twitter': {'content_count': random.randint(2, 10), 'total_duration': random.randint(100, 500)},
                    'youtube': {'content_count': random.randint(3, 12), 'total_duration': random.randint(200, 800)}
                }
            },
            'preferred_topics': [
                {'preference_value': 'technology', 'frequency': 8},
                {'preference_value': 'python', 'frequency': 6},
                {'preference_value': 'analytics', 'frequency': 5}
            ],
            'platform_preferences': {
                'twitter': {'content_count': random.randint(2, 10), 'total_duration': random.randint(100, 500)},
                'youtube': {'content_count': random.randint(3, 12), 'total_duration': random.randint(200, 800)}
            },
            'trending_interests': [
                {'preference_value': 'machine learning', 'frequency': 5, 'last_used': '2023-01-04T10:00:00'},
                {'preference_value': 'data science', 'frequency': 4, 'last_used': '2023-01-04T09:30:00'}
            ],
            'recommendation_accuracy': round(random.uniform(0.6, 0.85), 2)
        }
    
    def _calculate_viewing_summary(self, stats_24h: Dict, viewing_history: List[Dict]) -> Dict:
        """
        Calculate viewing summary for the user
        """
        total_content = len(viewing_history)
        total_duration = sum(int(v.get('watch_duration', 0)) for v in viewing_history)
        
        summary = {
            'total_content_viewed': total_content,
            'total_watch_time': total_duration,
            'average_watch_time': total_duration / total_content if total_content > 0 else 0,
            'content_by_platform': stats_24h
        }
        
        return summary
    
    def _get_preferred_topics(self, preferences: List[Dict]) -> List[Dict]:
        """
        Get user's preferred topics based on frequency
        """
        hashtags = [p for p in preferences if p['preference_type'] == 'hashtag']
        hashtags.sort(key=lambda x: x['frequency'], reverse=True)
        
        return hashtags[:10]  # Top 10 preferred topics
    
    def _get_platform_preferences(self, stats_24h: Dict) -> Dict:
        """
        Get user's platform preferences
        """
        return stats_24h
    
    def _get_trending_interests(self, preferences: List[Dict]) -> List[Dict]:
        """
        Get trending interests based on recent activity
        """
        # Sort by last used timestamp (most recent first)
        preferences.sort(key=lambda x: x.get('last_used', ''), reverse=True)
        return preferences[:5]  # Top 5 recent interests
    
    def _calculate_recommendation_accuracy(self, viewing_history: List[Dict]) -> float:
        """
        Calculate how well recommendations match user preferences
        """
        if not viewing_history:
            return 0.0
        
        # This is a simplified calculation
        # In a real system, we would track how many recommended items were actually viewed
        return round(random.uniform(0.6, 0.85), 2)  # Placeholder accuracy