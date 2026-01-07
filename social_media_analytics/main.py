#!/usr/bin/env python3
"""
Social Media Analytics Tool
Main script to collect, analyze, and visualize social media data
"""

import sys
import os
from datetime import datetime
from data_collector import collect_platform_data
from data_storage import DataStorage
from visualizer import SocialMediaVisualizer
from analyzer import SocialMediaAnalyzer


def main():
    print("Starting Social Media Analytics Tool...")
    print("="*50)
    
    # Initialize components
    storage = DataStorage()
    visualizer = SocialMediaVisualizer()
    analyzer = SocialMediaAnalyzer()
    
    # Collect data from Twitter (simulated)
    print("\nCollecting Twitter data...")
    try:
        twitter_data = collect_platform_data('twitter', 'sample_user', count=20)
        print(f"Collected {len(twitter_data['posts'])} tweets")
        
        # Store Twitter data
        storage.store_posts(twitter_data)
        storage.store_metrics(twitter_data)
        print("Twitter data stored successfully")
    except Exception as e:
        print(f"Error collecting Twitter data: {e}")
        twitter_data = None
    
    # Collect data from Reddit (simulated)
    print("\nCollecting Reddit data...")
    try:
        reddit_data = collect_platform_data('reddit', 'technology', count=20)
        print(f"Collected {len(reddit_data['posts'])} Reddit posts")
        
        # Store Reddit data
        storage.store_posts(reddit_data)
        storage.store_metrics(reddit_data)
        print("Reddit data stored successfully")
    except Exception as e:
        print(f"Error collecting Reddit data: {e}")
        reddit_data = None
    
    # Perform analysis
    print("\nPerforming analysis...")
    insights = []
    
    if twitter_data:
        print("\nTwitter Engagement Analysis:")
        tw_engagement = analyzer.analyze_engagement(twitter_data)
        for key, value in tw_engagement.items():
            print(f"  {key}: {value}")
        
        print("\nTwitter Audience Demographics:")
        tw_demographics = analyzer.analyze_audience_demographics(twitter_data)
        for key, value in tw_demographics.items():
            print(f"  {key}: {value}")
    
    if reddit_data:
        print("\nReddit Engagement Analysis:")
        rd_engagement = analyzer.analyze_engagement(reddit_data)
        for key, value in rd_engagement.items():
            print(f"  {key}: {value}")
        
        print("\nReddit Audience Demographics:")
        rd_demographics = analyzer.analyze_audience_demographics(reddit_data)
        for key, value in rd_demographics.items():
            print(f"  {key}: {value}")
    
    # Generate cross-platform insights
    print("\nCross-Platform Analysis:")
    comparison = analyzer.compare_platform_performance(twitter_data, reddit_data)
    if 'engagement_ratio' in comparison:
        ratio = comparison['engagement_ratio']
        print(f"  Twitter to Reddit engagement ratio: {ratio.get('twitter_to_reddit', 'N/A'):.2f}")
        print(f"  Reddit to Twitter engagement ratio: {ratio.get('reddit_to_twitter', 'N/A'):.2f}")
    
    # Generate actionable insights
    print("\nActionable Insights:")
    insights = analyzer.generate_insights(twitter_data, reddit_data)
    for i, insight in enumerate(insights, 1):
        print(f"  {i}. {insight}")
    
    # Create visualizations
    print("\nGenerating visualizations...")
    try:
        # Engagement comparison
        visualizer.plot_engagement_comparison(twitter_data, reddit_data)
        
        # Platform metrics
        visualizer.plot_platform_metrics(twitter_data, reddit_data)
        
        # Engagement trends
        visualizer.plot_engagement_trends(twitter_data, reddit_data)
        
        # Hashtag analysis (for Twitter)
        if twitter_data:
            visualizer.plot_hashtag_analysis(twitter_data)
        
        # Comprehensive dashboard
        visualizer.create_comprehensive_dashboard(twitter_data, reddit_data)
        
        print("Visualizations generated successfully")
    except Exception as e:
        print(f"Error generating visualizations: {e}")
    
    # Save results to a report
    print("\nGenerating report...")
    generate_report(twitter_data, reddit_data, insights)
    
    print("\nAnalytics complete!")
    print("="*50)


def generate_report(twitter_data, reddit_data, insights):
    """Generate a text report with findings"""
    report_filename = f"social_media_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    
    with open(report_filename, 'w', encoding='utf-8') as f:
        f.write("Social Media Analytics Report\n")
        f.write("="*50 + "\n")
        f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        if twitter_data:
            f.write("Twitter Analysis\n")
            f.write("-"*20 + "\n")
            f.write(f"Posts analyzed: {len(twitter_data['posts'])}\n")
            
            tw_engagement = SocialMediaAnalyzer().analyze_engagement(twitter_data)
            f.write(f"Average engagement: {tw_engagement.get('avg_engagement', 0)}\n")
            f.write(f"Average likes: {tw_engagement.get('avg_likes', 0)}\n")
            f.write(f"Average retweets: {tw_engagement.get('avg_retweets', 0)}\n")
            f.write(f"Average replies: {tw_engagement.get('avg_replies', 0)}\n\n")
        
        if reddit_data:
            f.write("Reddit Analysis\n")
            f.write("-"*20 + "\n")
            f.write(f"Posts analyzed: {len(reddit_data['posts'])}\n")
            
            rd_engagement = SocialMediaAnalyzer().analyze_engagement(reddit_data)
            f.write(f"Average engagement: {rd_engagement.get('avg_engagement', 0)}\n")
            f.write(f"Average upvotes: {rd_engagement.get('avg_upvotes', 0)}\n")
            f.write(f"Average comments: {rd_engagement.get('avg_comments', 0)}\n\n")
        
        f.write("Actionable Insights\n")
        f.write("-"*20 + "\n")
        for i, insight in enumerate(insights, 1):
            f.write(f"{i}. {insight}\n")
    
    print(f"Report saved to: {report_filename}")


if __name__ == "__main__":
    main()