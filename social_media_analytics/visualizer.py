import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from datetime import datetime
from typing import List, Dict
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

# Set style for matplotlib
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")


class SocialMediaVisualizer:
    """
    Creates visualizations for social media metrics and engagement
    """
    
    def __init__(self):
        self.colors = ['#1DA1F2', '#FF4500', '#3B5998', '#E1306C', '#25D366']  # Social media brand colors
    
    def plot_engagement_comparison(self, twitter_data: Dict, reddit_data: Dict):
        """Plot engagement comparison between Twitter and Reddit"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('Social Media Engagement Comparison', fontsize=16)
        
        # Twitter engagement metrics
        if twitter_data and 'posts' in twitter_data:
            twitter_posts = twitter_data['posts']
            twitter_likes = [p.get('likes', 0) for p in twitter_posts]
            twitter_retweets = [p.get('retweets', 0) for p in twitter_posts]
            twitter_replies = [p.get('replies', 0) for p in twitter_posts]
            
            # Twitter likes distribution
            axes[0, 0].hist(twitter_likes, bins=20, alpha=0.7, color=self.colors[0], label='Likes')
            axes[0, 0].set_title('Twitter Likes Distribution')
            axes[0, 0].set_xlabel('Number of Likes')
            axes[0, 0].set_ylabel('Frequency')
        
        # Reddit engagement metrics
        if reddit_data and 'posts' in reddit_data:
            reddit_posts = reddit_data['posts']
            reddit_upvotes = [p.get('upvotes', 0) for p in reddit_posts]
            reddit_comments = [p.get('comments', 0) for p in reddit_posts]
            
            # Reddit upvotes distribution
            axes[0, 1].hist(reddit_upvotes, bins=20, alpha=0.7, color=self.colors[1], label='Upvotes')
            axes[0, 1].set_title('Reddit Upvotes Distribution')
            axes[0, 1].set_xlabel('Number of Upvotes')
            axes[0, 1].set_ylabel('Frequency')
        
        # Engagement over time for Twitter
        if twitter_data and 'posts' in twitter_data:
            dates = [datetime.fromisoformat(p['timestamp'].replace('Z', '+00:00')) for p in twitter_posts]
            engagements = [p.get('likes', 0) + p.get('retweets', 0) + p.get('replies', 0) for p in twitter_posts]
            
            axes[1, 0].scatter(dates, engagements, alpha=0.7, color=self.colors[0])
            axes[1, 0].set_title('Twitter Engagement Over Time')
            axes[1, 0].set_xlabel('Date')
            axes[1, 0].set_ylabel('Engagement')
            axes[1, 0].tick_params(axis='x', rotation=45)
        
        # Engagement over time for Reddit
        if reddit_data and 'posts' in reddit_data:
            dates = [datetime.fromisoformat(p['timestamp'].replace('Z', '+00:00')) for p in reddit_posts]
            engagements = [p.get('upvotes', 0) + p.get('comments', 0) for p in reddit_posts]
            
            axes[1, 1].scatter(dates, engagements, alpha=0.7, color=self.colors[1])
            axes[1, 1].set_title('Reddit Engagement Over Time')
            axes[1, 1].set_xlabel('Date')
            axes[1, 1].set_ylabel('Engagement')
            axes[1, 1].tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        plt.show()
    
    def plot_platform_metrics(self, twitter_data: Dict, reddit_data: Dict):
        """Plot key metrics comparison between platforms"""
        fig, ax = plt.subplots(figsize=(12, 6))
        
        metrics = []
        values = []
        
        if twitter_data and 'metrics' in twitter_data:
            tw_metrics = twitter_data['metrics']
            metrics.extend(['Followers', 'Tweets Count'])
            values.extend([tw_metrics.get('followers', 0), tw_metrics.get('tweets_count', 0)])
        
        if reddit_data and 'metrics' in reddit_data:
            rd_metrics = reddit_data['metrics']
            metrics.extend(['Members', 'Active Users'])
            values.extend([rd_metrics.get('members', 0), rd_metrics.get('active_users', 0)])
        
        bars = ax.bar(metrics, values, color=[self.colors[0], self.colors[0], self.colors[1], self.colors[1]])
        ax.set_title('Platform Metrics Comparison')
        ax.set_ylabel('Count')
        
        # Add value labels on bars
        for bar, value in zip(bars, values):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{value:,}',
                   ha='center', va='bottom')
        
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()
    
    def plot_engagement_trends(self, twitter_data: Dict, reddit_data: Dict):
        """Plot engagement trends over time"""
        fig = go.Figure()
        
        # Twitter engagement trend
        if twitter_data and 'posts' in twitter_data:
            tw_posts = twitter_data['posts']
            dates = [p['timestamp'][:10] for p in tw_posts]  # Extract date part
            engagements = [p.get('likes', 0) + p.get('retweets', 0) + p.get('replies', 0) for p in tw_posts]
            
            fig.add_trace(go.Scatter(
                x=dates,
                y=engagements,
                mode='lines+markers',
                name='Twitter Engagement',
                line=dict(color=self.colors[0])
            ))
        
        # Reddit engagement trend
        if reddit_data and 'posts' in reddit_data:
            rd_posts = reddit_data['posts']
            dates = [p['timestamp'][:10] for p in rd_posts]  # Extract date part
            engagements = [p.get('upvotes', 0) + p.get('comments', 0) for p in rd_posts]
            
            fig.add_trace(go.Scatter(
                x=dates,
                y=engagements,
                mode='lines+markers',
                name='Reddit Engagement',
                line=dict(color=self.colors[1])
            ))
        
        fig.update_layout(
            title='Engagement Trends Over Time',
            xaxis_title='Date',
            yaxis_title='Engagement Score',
            hovermode='x unified'
        )
        
        fig.show()
    
    def plot_hashtag_analysis(self, twitter_data: Dict):
        """Plot hashtag frequency analysis for Twitter"""
        if not twitter_data or 'posts' not in twitter_data:
            return
        
        # Collect all hashtags from tweets
        all_hashtags = []
        for post in twitter_data['posts']:
            if 'hashtags' in post and post['hashtags']:
                all_hashtags.extend(post['hashtags'])
        
        # Count hashtag frequencies
        hashtag_counts = {}
        for tag in all_hashtags:
            hashtag_counts[tag] = hashtag_counts.get(tag, 0) + 1
        
        # Sort by frequency
        sorted_hashtags = sorted(hashtag_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        if not sorted_hashtags:
            print("No hashtags found in the data.")
            return
        
        hashtags, counts = zip(*sorted_hashtags)
        
        plt.figure(figsize=(12, 6))
        bars = plt.bar(hashtags, counts, color=self.colors[0])
        plt.title('Top 10 Hashtags by Frequency')
        plt.xlabel('Hashtags')
        plt.ylabel('Frequency')
        plt.xticks(rotation=45)
        
        # Add value labels on bars
        for bar, count in zip(bars, counts):
            plt.text(bar.get_x() + bar.get_width()/2., bar.get_height(),
                    f'{count}', ha='center', va='bottom')
        
        plt.tight_layout()
        plt.show()
    
    def create_comprehensive_dashboard(self, twitter_data: Dict, reddit_data: Dict):
        """Create a comprehensive dashboard with multiple visualizations"""
        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Twitter Engagement Over Time', 'Reddit Engagement Over Time', 
                           'Platform Metrics', 'Hashtag Analysis'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        # Twitter engagement over time
        if twitter_data and 'posts' in twitter_data:
            tw_posts = twitter_data['posts']
            dates = [p['timestamp'][:10] for p in tw_posts]
            engagements = [p.get('likes', 0) + p.get('retweets', 0) + p.get('replies', 0) for p in tw_posts]
            
            fig.add_trace(
                go.Scatter(x=dates, y=engagements, mode='lines+markers', name='Twitter', line=dict(color=self.colors[0])),
                row=1, col=1
            )
        
        # Reddit engagement over time
        if reddit_data and 'posts' in reddit_data:
            rd_posts = reddit_data['posts']
            dates = [p['timestamp'][:10] for p in rd_posts]
            engagements = [p.get('upvotes', 0) + p.get('comments', 0) for p in rd_posts]
            
            fig.add_trace(
                go.Scatter(x=dates, y=engagements, mode='lines+markers', name='Reddit', line=dict(color=self.colors[1])),
                row=1, col=2
            )
        
        # Platform metrics
        if twitter_data and 'metrics' in twitter_data and reddit_data and 'metrics' in reddit_data:
            fig.add_trace(
                go.Bar(x=['Twitter Followers', 'Reddit Members'], 
                      y=[twitter_data['metrics'].get('followers', 0), 
                         reddit_data['metrics'].get('members', 0)],
                      name='Metrics',
                      marker_color=[self.colors[0], self.colors[1]]),
                row=2, col=1
            )
        
        # Hashtag analysis
        if twitter_data and 'posts' in twitter_data:
            # Collect hashtags
            all_hashtags = []
            for post in twitter_data['posts']:
                if 'hashtags' in post and post['hashtags']:
                    all_hashtags.extend(post['hashtags'])
            
            # Count frequencies
            hashtag_counts = {}
            for tag in all_hashtags:
                hashtag_counts[tag] = hashtag_counts.get(tag, 0) + 1
            
            # Top 5 hashtags
            sorted_hashtags = sorted(hashtag_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            
            if sorted_hashtags:
                hashtags, counts = zip(*sorted_hashtags)
                fig.add_trace(
                    go.Bar(x=list(hashtags), y=list(counts), name='Hashtags', marker_color=self.colors[0]),
                    row=2, col=2
                )
        
        fig.update_layout(height=800, showlegend=True, title_text="Social Media Analytics Dashboard")
        fig.show()