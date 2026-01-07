"""
Report generation module for social media analytics
Creates detailed reports based on collected data
"""

import os
from datetime import datetime
from typing import Dict, List
import json
from data_storage import DataStorage
from analyzer import SocialMediaAnalyzer


class ReportGenerator:
    """
    Generates detailed reports based on social media analytics data
    """
    
    def __init__(self, storage: DataStorage = None, analyzer: SocialMediaAnalyzer = None):
        self.storage = storage or DataStorage()
        self.analyzer = analyzer or SocialMediaAnalyzer()
        self.report_directory = "reports"
        
        # Create reports directory if it doesn't exist
        os.makedirs(self.report_directory, exist_ok=True)

    def generate_platform_report(self, platform: str) -> Dict:
        """
        Generate a detailed report for a specific platform
        """
        # Get posts and metrics for the platform
        posts = self.storage.get_posts_by_platform(platform)
        metrics = self.storage.get_metrics_by_platform(platform)
        
        # Perform engagement analysis
        platform_data = {
            'platform': platform,
            'posts': posts,
            'metrics': {m['metric_type']: m['value'] for m in metrics}
        }
        
        engagement_analysis = self.analyzer.analyze_engagement(platform_data)
        audience_demographics = self.analyzer.analyze_audience_demographics(platform_data)
        peak_times = self.analyzer.get_peak_times(platform_data)
        
        # Generate insights
        insights = self._generate_platform_insights(platform_data, engagement_analysis, audience_demographics)
        
        report = {
            'platform': platform,
            'generated_at': datetime.now().isoformat(),
            'engagement_analysis': engagement_analysis,
            'audience_demographics': audience_demographics,
            'peak_times': peak_times,
            'insights': insights,
            'total_posts': len(posts),
            'total_metrics': len(metrics)
        }
        
        return report

    def generate_comparison_report(self, platforms: List[str] = ['Twitter', 'YouTube']) -> Dict:
        """
        Generate a comparison report between multiple platforms
        """
        platform_reports = {}
        
        for platform in platforms:
            platform_reports[platform] = self.generate_platform_report(platform)
        
        # Get cross-platform insights
        insights = self._generate_cross_platform_insights(platform_reports)
        
        report = {
            'generated_at': datetime.now().isoformat(),
            'platforms': platform_reports,
            'cross_platform_insights': insights,
            'comparison_summary': self._create_comparison_summary(platform_reports)
        }
        
        return report

    def generate_trending_report(self) -> Dict:
        """
        Generate a report on trending hashtags and topics
        """
        trending_hashtags = self.storage.get_trending_hashtags(hours=24, limit=20)
        
        report = {
            'generated_at': datetime.now().isoformat(),
            'trending_hashtags': trending_hashtags,
            'trending_summary': self._create_trending_summary(trending_hashtags)
        }
        
        return report

    def save_report_to_file(self, report: Dict, report_type: str, filename: str = None) -> str:
        """
        Save a report to a file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"social_media_report_{report_type}_{timestamp}.json"
        
        filepath = os.path.join(self.report_directory, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        return filepath

    def generate_text_report(self, report_data: Dict) -> str:
        """
        Generate a human-readable text report
        """
        report_lines = []
        report_lines.append("="*60)
        report_lines.append("SOCIAL MEDIA ANALYTICS REPORT")
        report_lines.append("="*60)
        report_lines.append(f"Generated at: {report_data.get('generated_at', 'N/A')}")
        report_lines.append("")
        
        if 'platform' in report_data:  # Single platform report
            platform = report_data['platform']
            report_lines.append(f"PLATFORM: {platform.upper()}")
            report_lines.append("-" * 40)
            
            # Engagement analysis
            engagement = report_data.get('engagement_analysis', {})
            report_lines.append("ENGAGEMENT ANALYSIS:")
            report_lines.append(f"  Total Posts: {report_data.get('total_posts', 0)}")
            report_lines.append(f"  Average Engagement: {engagement.get('avg_engagement', 0)}")
            report_lines.append(f"  Median Engagement: {engagement.get('median_engagement', 0)}")
            report_lines.append(f"  Max Engagement: {engagement.get('max_engagement', 0)}")
            report_lines.append("")
            
            # Audience demographics
            demographics = report_data.get('audience_demographics', {})
            report_lines.append("AUDIENCE DEMOGRAPHICS:")
            top_locations = demographics.get('top_locations', {})
            if top_locations:
                report_lines.append("  Top Locations:")
                for location, count in list(top_locations.items())[:5]:
                    report_lines.append(f"    - {location}: {count}")
            
            peak_hours = demographics.get('peak_activity_hours', {})
            if peak_hours:
                report_lines.append("  Peak Activity Hours:")
                for hour, count in list(peak_hours.items())[:5]:
                    report_lines.append(f"    - {hour}:00: {count}")
            
            top_hashtags = demographics.get('top_hashtags', {})
            if top_hashtags:
                report_lines.append("  Top Hashtags:")
                for hashtag, count in list(top_hashtags.items())[:10]:
                    report_lines.append(f"    - {hashtag}: {count}")
            report_lines.append("")
            
            # Insights
            insights = report_data.get('insights', [])
            if insights:
                report_lines.append("ACTIONABLE INSIGHTS:")
                for i, insight in enumerate(insights, 1):
                    report_lines.append(f"  {i}. {insight}")
            report_lines.append("")
        
        elif 'platforms' in report_data:  # Comparison report
            report_lines.append("CROSS-PLATFORM COMPARISON REPORT")
            report_lines.append("-" * 40)
            
            for platform, data in report_data['platforms'].items():
                report_lines.append(f"{platform.upper()}:")
                engagement = data.get('engagement_analysis', {})
                report_lines.append(f"  Average Engagement: {engagement.get('avg_engagement', 0)}")
                report_lines.append(f"  Total Posts: {data.get('total_posts', 0)}")
                report_lines.append("")
            
            # Cross-platform insights
            cross_insights = report_data.get('cross_platform_insights', [])
            if cross_insights:
                report_lines.append("CROSS-PLATFORM INSIGHTS:")
                for i, insight in enumerate(cross_insights, 1):
                    report_lines.append(f"  {i}. {insight}")
            report_lines.append("")
        
        elif 'trending_hashtags' in report_data:  # Trending report
            report_lines.append("TRENDING HASHTAGS REPORT")
            report_lines.append("-" * 40)
            
            hashtags = report_data['trending_hashtags']
            report_lines.append("TOP TRENDING HASHTAGS:")
            for i, hashtag_data in enumerate(hashtags[:10], 1):
                report_lines.append(f"  {i}. {hashtag_data['hashtag']} ({hashtag_data['count']} mentions)")
            report_lines.append("")
        
        report_lines.append("="*60)
        
        return "\n".join(report_lines)

    def save_text_report(self, report_data: Dict, report_type: str, filename: str = None) -> str:
        """
        Save a human-readable text report to a file
        """
        text_report = self.generate_text_report(report_data)
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"social_media_report_{report_type}_{timestamp}.txt"
        
        filepath = os.path.join(self.report_directory, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(text_report)
        
        return filepath

    def _generate_platform_insights(self, platform_data: Dict, engagement_analysis: Dict, demographics: Dict) -> List[str]:
        """
        Generate platform-specific insights
        """
        insights = []
        platform = platform_data['platform'].lower()
        
        # Engagement-based insights
        avg_engagement = engagement_analysis.get('avg_engagement', 0)
        if avg_engagement > 100:
            insights.append(f"{platform.capitalize()} shows high engagement (avg: {avg_engagement:.2f}). Keep creating similar content.")
        elif avg_engagement < 50:
            insights.append(f"{platform.capitalize()} engagement is low (avg: {avg_engagement:.2f}). Consider changing content strategy.")
        
        # Demographic insights
        top_locations = demographics.get('top_locations', {})
        if top_locations:
            top_location = next(iter(top_locations))
            insights.append(f"Most of your {platform} audience is from {top_location}. Target content to this region.")
        
        peak_hour = demographics.get('most_active_hour')
        if peak_hour is not None:
            insights.append(f"Your {platform} audience is most active at {peak_hour}:00. Post during this time for maximum reach.")
        
        # Hashtag insights
        top_hashtags = demographics.get('top_hashtags', {})
        if top_hashtags:
            top_hashtag = next(iter(top_hashtags))
            insights.append(f"Your most popular hashtag is {top_hashtag}. Use this and similar hashtags more often.")
        
        return insights

    def _generate_cross_platform_insights(self, platform_reports: Dict) -> List[str]:
        """
        Generate insights comparing multiple platforms
        """
        insights = []
        
        if 'Twitter' in platform_reports and 'YouTube' in platform_reports:
            tw_avg_engagement = platform_reports['Twitter']['engagement_analysis'].get('avg_engagement', 0)
            yt_avg_engagement = platform_reports['YouTube']['engagement_analysis'].get('avg_engagement', 0)
            
            if tw_avg_engagement > yt_avg_engagement * 2:
                insights.append("Twitter performs significantly better than YouTube. Consider focusing more resources on Twitter.")
            elif yt_avg_engagement > tw_avg_engagement * 2:
                insights.append("YouTube performs significantly better than Twitter. Consider focusing more resources on YouTube.")
            
            tw_posts = platform_reports['Twitter']['total_posts']
            yt_posts = platform_reports['YouTube']['total_posts']
            
            if tw_posts > yt_posts * 2:
                insights.append("You're posting much more frequently on Twitter than YouTube. Consider balancing your content distribution.")
            elif yt_posts > tw_posts * 2:
                insights.append("You're posting much more frequently on YouTube than Twitter. Consider balancing your content distribution.")
        
        return insights

    def _create_comparison_summary(self, platform_reports: Dict) -> Dict:
        """
        Create a summary comparing platforms
        """
        summary = {}
        
        for platform, report in platform_reports.items():
            summary[platform] = {
                'total_posts': report.get('total_posts', 0),
                'avg_engagement': report.get('engagement_analysis', {}).get('avg_engagement', 0),
                'total_metrics': report.get('total_metrics', 0)
            }
        
        return summary

    def _create_trending_summary(self, trending_hashtags: List[Dict]) -> Dict:
        """
        Create a summary of trending hashtags
        """
        if not trending_hashtags:
            return {
                'total_trending': 0,
                'top_hashtag': None
            }
        
        return {
            'total_trending': len(trending_hashtags),
            'top_hashtag': trending_hashtags[0]['hashtag'] if trending_hashtags else None
        }


def generate_full_report():
    """
    Generate a comprehensive report combining all analytics
    """
    storage = DataStorage()
    analyzer = SocialMediaAnalyzer()
    generator = ReportGenerator(storage, analyzer)
    
    # Generate individual reports
    twitter_report = generator.generate_platform_report('Twitter')
    youtube_report = generator.generate_platform_report('YouTube')
    comparison_report = generator.generate_comparison_report()
    trending_report = generator.generate_trending_report()
    
    # Combine into a full report
    full_report = {
        'generated_at': datetime.now().isoformat(),
        'twitter_report': twitter_report,
        'youtube_report': youtube_report,
        'comparison_report': comparison_report,
        'trending_report': trending_report
    }
    
    # Save the full report
    json_path = generator.save_report_to_file(full_report, 'full')
    text_path = generator.save_text_report(full_report, 'full')
    
    print(f"Full report generated:")
    print(f"  JSON: {json_path}")
    print(f"  Text: {text_path}")
    
    return full_report