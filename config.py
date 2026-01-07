"""
Configuration module for social media analytics tool
Handles API credentials and application settings
"""

import os
from typing import Dict, Optional
from dataclasses import dataclass
import json


@dataclass
class TwitterConfig:
    """Configuration for Twitter API"""
    bearer_token: str
    api_key: str
    api_secret: str
    access_token: str
    access_token_secret: str

    @classmethod
    def from_env(cls) -> 'TwitterConfig':
        """Create TwitterConfig from environment variables"""
        return cls(
            bearer_token=os.getenv('AAAAAAAAAAAAAAAAAAAAAE9I5gEAAAAAiNRbw9qk4ntUmUOgpN8S73fymXY%3DZ9lfIUsu1e8LZsGXbPbhGwnkzG5WKp8RQGbgy3JtH877wADc87', ''),
            api_key=os.getenv('97DKzt9UYpFNxhgOJy04NP9NW', ''),
            api_secret=os.getenv('39c1WZG2ka66zZIk687WcHgw1Fm5wgGsAadTCpsUlhmugXX3YA', ''),
            access_token=os.getenv('1499087836938657793-rynXx27qkDUn0Oub6T6OjpboLJHtPE', ''),
            access_token_secret=os.getenv('rOcm5iDXQPDoEFxJQGiQYZ5cNW5bLvA3rfUWf2hpvzHpo', '')
        )

    @classmethod
    def from_dict(cls, data: Dict) -> 'TwitterConfig':
        """Create TwitterConfig from dictionary"""
        return cls(
            bearer_token=data.get('bearer_token', ''),
            api_key=data.get('api_key', ''),
            api_secret=data.get('api_secret', ''),
            access_token=data.get('access_token', ''),
            access_token_secret=data.get('access_token_secret', '')
        )


@dataclass
class YouTubeConfig:
    """Configuration for YouTube API"""
    api_key: str

    @classmethod
    def from_env(cls) -> 'YouTubeConfig':
        """Create YouTubeConfig from environment variables"""
        return cls(
            api_key=os.getenv('AIzaSyAb3A89r-XB2M-6arR_4YHMACB3ca4-wn8', '')
        )

    @classmethod
    def from_dict(cls, data: Dict) -> 'YouTubeConfig':
        """Create YouTubeConfig from dictionary"""
        return cls(
            api_key=data.get('api_key', '')
        )




@dataclass
class PersonalTrackingConfig:
    """Configuration for personal tracking features"""
    enable_viewing_tracking: bool = True
    max_viewing_history_days: int = 30
    recommendation_update_interval: int = 300  # seconds
    privacy_mode: bool = False
    browser_extension_api_key: str = ""  # For browser extension authentication

@dataclass
class AppConfig:
    """Main application configuration"""
    twitter: TwitterConfig
    youtube: YouTubeConfig
    personal_tracking: PersonalTrackingConfig
    database_path: str = "social_media_data.db"
    report_directory: str = "reports"
    max_posts_per_request: int = 50
    request_delay: float = 1.0  # seconds between API requests

    @classmethod
    def load_from_file(cls, config_path: str = "config.json") -> 'AppConfig':
        """Load configuration from JSON file"""
        if not os.path.exists(config_path):
            # Create a default config file if it doesn't exist
            cls.create_default_config(config_path)
            print(f"Created default configuration file at {config_path}")
            print("Please update the API credentials in the file before running the application.")
            return cls.create_default_config_obj()

        with open(config_path, 'r') as f:
            data = json.load(f)

        twitter_config = TwitterConfig.from_dict(data.get('twitter', {}))
        youtube_config = YouTubeConfig.from_dict(data.get('youtube', {}))
        personal_tracking_config = PersonalTrackingConfig(
            enable_viewing_tracking=data.get('enable_viewing_tracking', True),
            max_viewing_history_days=data.get('max_viewing_history_days', 30),
            recommendation_update_interval=data.get('recommendation_update_interval', 300),
            privacy_mode=data.get('privacy_mode', False),
            browser_extension_api_key=data.get('browser_extension_api_key', '')
        )

        return cls(
            twitter=twitter_config,
            youtube=youtube_config,
            personal_tracking=personal_tracking_config,
            database_path=data.get('database_path', 'social_media_data.db'),
            report_directory=data.get('report_directory', 'reports'),
            max_posts_per_request=data.get('max_posts_per_request', 50),
            request_delay=data.get('request_delay', 1.0)
        )

    @classmethod
    def create_default_config(cls, config_path: str = "config.json") -> None:
        """Create a default configuration file"""
        default_config = {
            "twitter": {
                "bearer_token": "AAAAAAAAAAAAAAAAAAAAAE9I5gEAAAAAiNRbw9qk4ntUmUOgpN8S73fymXY%3DZ9lfIUsu1e8LZsGXbPbhGwnkzG5WKp8RQGbgy3JtH877wADc87",
                "api_key": "97DKzt9UYpFNxhgOJy04NP9NW",
                "api_secret": "39c1WZG2ka66zZIk687WcHgw1Fm5wgGsAadTCpsUlhmugXX3YA",
                "access_token": "1499087836938657793-rynXx27qkDUn0Oub6T6OjpboLJHtPE",
                "access_token_secret": "rOcm5iDXQPDoEFxJQGiQYZ5cNW5bLvA3rfUWf2hpvzHpo"
            },
            "youtube": {
                "api_key": "AIzaSyAb3A89r-XB2M-6arR_4YHMACB3ca4-wn8"
            },
            "enable_viewing_tracking": True,
            "max_viewing_history_days": 30,
            "recommendation_update_interval": 300,
            "privacy_mode": False,
            "browser_extension_api_key": "",
            "content_discovery_api_key": "",
            "database_path": "social_media_data.db",
            "report_directory": "reports",
            "max_posts_per_request": 50,
            "request_delay": 1.0
        }

        with open(config_path, 'w') as f:
            json.dump(default_config, f, indent=4)

    @classmethod
    def create_default_config_obj(cls) -> 'AppConfig':
        """Create a default configuration object with empty credentials"""
        return cls(
            twitter=TwitterConfig("", "", "", "", ""),
            youtube=YouTubeConfig(""),
            personal_tracking=PersonalTrackingConfig(),
            database_path="social_media_data.db",
            report_directory="reports",
            max_posts_per_request=50,
            request_delay=1.0
        )

    def validate(self) -> bool:
        """Validate that all required configuration values are present"""
        errors = []

        if not self.twitter.bearer_token:
            errors.append("Twitter bearer token is missing")
        if not self.twitter.api_key:
            errors.append("Twitter API key is missing")
        if not self.twitter.api_secret:
            errors.append("Twitter API secret is missing")
        if not self.twitter.access_token:
            errors.append("Twitter access token is missing")
        if not self.twitter.access_token_secret:
            errors.append("Twitter access token secret is missing")
        if not self.youtube.api_key:
            errors.append("YouTube API key is missing")
        if not self.personal_tracking.browser_extension_api_key and self.personal_tracking.enable_viewing_tracking:
            errors.append("Browser extension API key is missing (required when viewing tracking is enabled)")

        if errors:
            print("Configuration validation errors:")
            for error in errors:
                print(f"  - {error}")
            return False

        return True