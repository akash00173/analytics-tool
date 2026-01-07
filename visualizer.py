import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from datetime import datetime
from typing import List, Dict
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import threading
import time
import json

# Set style for matplotlib
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")


class SocialMediaVisualizer:
    """
    Creates visualizations for social media metrics and engagement
    """

    def __init__(self):
        self.colors = ['#1DA1F2', '#FF4500', '#3B5998', '#E1306C', '#25D366']  # Social media brand colors
        # Store data for real-time updates
        self.twitter_data_buffer = []
        self.reddit_data_buffer = []
        self.realtime_fig = None
        self.realtime_active = False

    def plot_engagement_comparison(self, twitter_data: Dict, youtube_data: Dict):
        """Plot engagement comparison between Twitter and YouTube"""
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

        # YouTube engagement metrics
        if youtube_data and 'posts' in youtube_data:
            youtube_posts = youtube_data['posts']
            youtube_views = [p.get('views', 0) for p in youtube_posts]
            youtube_likes = [p.get('likes', 0) for p in youtube_posts]
            youtube_comments = [p.get('comments', 0) for p in youtube_posts]

            # YouTube views distribution
            axes[0, 1].hist(youtube_views, bins=20, alpha=0.7, color=self.colors[1], label='Views')
            axes[0, 1].set_title('YouTube Views Distribution')
            axes[0, 1].set_xlabel('Number of Views')
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

        # Engagement over time for YouTube
        if youtube_data and 'posts' in youtube_data:
            dates = [datetime.fromisoformat(p['timestamp'].replace('Z', '+00:00')) for p in youtube_posts]
            engagements = [p.get('likes', 0) + p.get('comments', 0) for p in youtube_posts]

            axes[1, 1].scatter(dates, engagements, alpha=0.7, color=self.colors[1])
            axes[1, 1].set_title('YouTube Engagement Over Time')
            axes[1, 1].set_xlabel('Date')
            axes[1, 1].set_ylabel('Engagement')
            axes[1, 1].tick_params(axis='x', rotation=45)

        plt.tight_layout()
        plt.show()

    def plot_platform_metrics(self, twitter_data: Dict, youtube_data: Dict):
        """Plot key metrics comparison between platforms"""
        fig, ax = plt.subplots(figsize=(12, 6))

        metrics = []
        values = []

        if twitter_data and 'metrics' in twitter_data:
            tw_metrics = twitter_data['metrics']
            metrics.extend(['Followers', 'Tweets Count'])
            values.extend([tw_metrics.get('followers', 0), tw_metrics.get('tweets_count', 0)])

        if youtube_data and 'metrics' in youtube_data:
            yt_metrics = youtube_data['metrics']
            metrics.extend(['Subscribers', 'Total Videos'])
            values.extend([yt_metrics.get('subscribers', 0), yt_metrics.get('total_videos', 0)])

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

    def plot_engagement_trends(self, twitter_data: Dict, youtube_data: Dict):
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

        # YouTube engagement trend
        if youtube_data and 'posts' in youtube_data:
            yt_posts = youtube_data['posts']
            dates = [p['timestamp'][:10] for p in yt_posts]  # Extract date part
            engagements = [p.get('likes', 0) + p.get('comments', 0) for p in yt_posts]

            fig.add_trace(go.Scatter(
                x=dates,
                y=engagements,
                mode='lines+markers',
                name='YouTube Engagement',
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

    def create_comprehensive_dashboard(self, twitter_data: Dict, youtube_data: Dict):
        """Create a comprehensive dashboard with multiple visualizations"""
        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Twitter Engagement Over Time', 'YouTube Engagement Over Time',
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

        # YouTube engagement over time
        if youtube_data and 'posts' in youtube_data:
            yt_posts = youtube_data['posts']
            dates = [p['timestamp'][:10] for p in yt_posts]
            engagements = [p.get('likes', 0) + p.get('comments', 0) for p in yt_posts]

            fig.add_trace(
                go.Scatter(x=dates, y=engagements, mode='lines+markers', name='YouTube', line=dict(color=self.colors[1])),
                row=1, col=2
            )

        # Platform metrics
        if twitter_data and 'metrics' in twitter_data and youtube_data and 'metrics' in youtube_data:
            fig.add_trace(
                go.Bar(x=['Twitter Followers', 'YouTube Subscribers'],
                      y=[twitter_data['metrics'].get('followers', 0),
                         youtube_data['metrics'].get('subscribers', 0)],
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

    def start_realtime_visualization(self):
        """Start real-time visualization dashboard"""
        print("Starting real-time visualization dashboard...")

        # Create an initial figure for real-time updates
        self.realtime_fig = go.Figure()
        self.realtime_fig.update_layout(
            title='Real-Time Social Media Analytics Dashboard',
            xaxis_title='Time',
            yaxis_title='Engagement Score',
            hovermode='x unified'
        )

        # Show an empty figure initially
        self.realtime_fig.show()

        # Update the figure in a separate thread
        self.realtime_active = True
        update_thread = threading.Thread(target=self._update_realtime_figures, daemon=True)
        update_thread.start()

        print("Real-time visualization started.")

    def stop_realtime_visualization(self):
        """Stop real-time visualization"""
        self.realtime_active = False
        print("Real-time visualization stopped.")

    def _update_realtime_figures(self):
        """Update the real-time figures with new data"""
        while self.realtime_active:
            # Update the engagement trends plot with new data
            self._update_engagement_trends()

            # Sleep for a short time before updating again
            time.sleep(5)  # Update every 5 seconds

    def _update_engagement_trends(self):
        """Update the engagement trends with the latest data"""
        # This would be updated with new data as it comes in
        # For now, we'll just update the existing figure with mock data
        pass

    def add_realtime_data(self, platform: str, post_data: Dict):
        """Add real-time data to the visualization buffers"""
        # Add data to the appropriate buffer
        if platform.lower() == 'twitter':
            self.twitter_data_buffer.append(post_data)
            # Keep only the most recent 100 entries
            if len(self.twitter_data_buffer) > 100:
                self.twitter_data_buffer = self.twitter_data_buffer[-100:]
        elif platform.lower() == 'reddit':
            self.reddit_data_buffer.append(post_data)
            # Keep only the most recent 100 entries
            if len(self.reddit_data_buffer) > 100:
                self.reddit_data_buffer = self.reddit_data_buffer[-100:]

    def create_realtime_dashboard(self, update_callback=None):
        """Create a real-time dashboard that can be updated with new data"""
        # Create a dashboard with subplots for real-time updates
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Live Twitter Engagement', 'Live YouTube Engagement',
                           'Platform Comparison', 'Trending Hashtags'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}]]
        )

        # Set layout
        fig.update_layout(
            title_text="Real-Time Social Media Analytics Dashboard",
            height=800,
            showlegend=True
        )

        # Initial empty traces for each subplot
        fig.add_trace(go.Scatter(x=[], y=[], mode='lines+markers', name='Twitter', line=dict(color=self.colors[0])),
                      row=1, col=1)
        fig.add_trace(go.Scatter(x=[], y=[], mode='lines+markers', name='Reddit', line=dict(color=self.colors[1])),
                      row=1, col=2)
        fig.add_trace(go.Bar(x=[], y=[], name='Metrics'), row=2, col=1)
        fig.add_trace(go.Bar(x=[], y=[], name='Hashtags'), row=2, col=2)

        # Show the initial figure
        fig.show()

        # If an update callback is provided, call it periodically
        if update_callback:
            update_thread = threading.Thread(target=self._run_update_loop,
                                           args=(fig, update_callback), daemon=True)
            update_thread.start()

        return fig

    def _run_update_loop(self, fig, update_callback):
        """Run the update loop for real-time dashboard"""
        while self.realtime_active:
            # Call the update callback to get new data
            new_data = update_callback()

            # Update the dashboard with new data
            self._update_dashboard_with_data(fig, new_data)

            # Sleep before next update
            time.sleep(2)  # Update every 2 seconds

    def _update_dashboard_with_data(self, fig, new_data):
        """Update the dashboard with new data"""
        # This would update the dashboard with real-time data
        # Implementation would depend on the specific data format
        pass


class RealTimeDashboard:
    """
    A real-time dashboard that can be updated with new data as it comes in
    """
    def __init__(self):
        self.visualizer = SocialMediaVisualizer()
        self.data_points = {'twitter': [], 'reddit': []}
        self.lock = threading.Lock()

    def start_dashboard(self):
        """Start the real-time dashboard"""
        self.visualizer.start_realtime_visualization()

    def stop_dashboard(self):
        """Stop the real-time dashboard"""
        self.visualizer.stop_realtime_visualization()

    def update_with_post(self, post_data):
        """Update the dashboard with a new post"""
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

        # Add to data points with timestamp
        with self.lock:
            self.data_points[platform].append({
                'timestamp': datetime.now().isoformat(),
                'engagement_score': engagement_score,
                'post_data': post
            })

            # Keep only the most recent 50 data points
            if len(self.data_points[platform]) > 50:
                self.data_points[platform] = self.data_points[platform][-50:]

        # Add to visualizer buffer
        self.visualizer.add_realtime_data(platform, {
            'timestamp': datetime.now().isoformat(),
            'engagement_score': engagement_score
        })