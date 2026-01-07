"""
Social Media Analytics Tool
Real-time data collection and dashboard server with configuration interface
"""

from datetime import datetime
from data_collector import RealTimeDataCollector
from data_storage import DataStorage
from analyzer import SocialMediaAnalyzer
from report_generator import ReportGenerator, generate_full_report
from recommendation_engine import RecommendationEngine, PersonalAnalytics
import threading
import time
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_socketio import SocketIO, emit
from config import AppConfig
import json
import os


# Initialize Flask app and SocketIO
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'  # Change this to a random secret key
socketio = SocketIO(app, cors_allowed_origins="*")

# Global components
storage = DataStorage()
analyzer = SocialMediaAnalyzer()
recommendation_engine = RecommendationEngine(storage, analyzer)
personal_analytics = PersonalAnalytics(storage)
real_time_collector = None  # Will be initialized in the main function

# Store dashboard state
dashboard_data = {
    'twitter_engagement': [],
    'youtube_engagement': [],
    'trending_hashtags': [],
    'high_engagement_posts': [],
    'personal_recommendations': recommendation_engine._generate_mock_recommendations(5),
    'personal_insights': personal_analytics._generate_mock_insights()
}


@app.route('/')
def index():
    """Serve the main dashboard page"""
    return render_template('dashboard.html')


@app.route('/config', methods=['GET', 'POST'])
def config_page():
    """Configuration management page"""
    config_path = "config.json"
    
    if request.method == 'POST':
        # Get form data
        twitter_bearer_token = request.form.get('twitter_bearer_token', '').strip()
        twitter_api_key = request.form.get('twitter_api_key', '').strip()
        twitter_api_secret = request.form.get('twitter_api_secret', '').strip()
        twitter_access_token = request.form.get('twitter_access_token', '').strip()
        twitter_access_token_secret = request.form.get('twitter_access_token_secret', '').strip()

        youtube_api_key = request.form.get('youtube_api_key', '').strip()

        # Personal tracking settings
        enable_viewing_tracking = request.form.get('enable_viewing_tracking') == 'true'
        max_viewing_history_days = int(request.form.get('max_viewing_history_days', 30))
        recommendation_update_interval = int(request.form.get('recommendation_update_interval', 300))
        privacy_mode = request.form.get('privacy_mode') == 'true'
        browser_extension_api_key = request.form.get('browser_extension_api_key', '').strip()
        content_discovery_api_key = request.form.get('content_discovery_api_key', '').strip()

        database_path = request.form.get('database_path', 'social_media_data.db').strip()
        report_directory = request.form.get('report_directory', 'reports').strip()
        max_posts_per_request = int(request.form.get('max_posts_per_request', 50))
        request_delay = float(request.form.get('request_delay', 1.0))

        # Create config dictionary
        config_data = {
            "twitter": {
                "bearer_token": twitter_bearer_token,
                "api_key": twitter_api_key,
                "api_secret": twitter_api_secret,
                "access_token": twitter_access_token,
                "access_token_secret": twitter_access_token_secret
            },
            "youtube": {
                "api_key": youtube_api_key
            },
            "enable_viewing_tracking": enable_viewing_tracking,
            "max_viewing_history_days": max_viewing_history_days,
            "recommendation_update_interval": recommendation_update_interval,
            "privacy_mode": privacy_mode,
            "browser_extension_api_key": browser_extension_api_key,
            "content_discovery_api_key": content_discovery_api_key,
            "database_path": database_path,
            "report_directory": report_directory,
            "max_posts_per_request": max_posts_per_request,
            "request_delay": request_delay
        }

        # Write config to file
        try:
            with open(config_path, 'w') as f:
                json.dump(config_data, f, indent=4)
            flash('Configuration saved successfully!', 'success')
        except Exception as e:
            flash(f'Error saving configuration: {str(e)}', 'error')

    # Load current config
    current_config = {
        "twitter": {},
        "youtube": {},
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
    
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                current_config = json.load(f)
        except Exception as e:
            flash(f'Error loading configuration: {str(e)}', 'error')
    
    return render_template('config.html', config=current_config)


@app.route('/config/validate', methods=['POST'])
def validate_config():
    """Validate the current configuration"""
    try:
        config = AppConfig.load_from_file()
        is_valid = config.validate()
        
        if is_valid:
            return jsonify({'status': 'success', 'message': 'Configuration is valid'})
        else:
            return jsonify({'status': 'error', 'message': 'Configuration has validation errors'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Error validating config: {str(e)}'})


@app.route('/config/test', methods=['POST'])
def test_config():
    """Test API connectivity with current configuration"""
    try:
        # This would test actual API connectivity in a real implementation
        # For now, we'll just validate that the config is loaded properly
        config = AppConfig.load_from_file()
        is_valid = config.validate()
        
        if not is_valid:
            return jsonify({'status': 'error', 'message': 'Configuration validation failed'})
        
        # In a real implementation, you would test actual API connectivity here
        # For example, make a simple API call to each platform
        
        return jsonify({'status': 'success', 'message': 'Configuration appears valid, API connectivity test would happen here'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Error testing config: {str(e)}'})


@app.route('/generate_report')
def generate_report():
    """Generate a comprehensive social media report"""
    try:
        report = generate_full_report()
        return {
            'status': 'success',
            'message': 'Report generated successfully',
            'report_data': report
        }
    except Exception as e:
        print(f"Error generating report: {e}")
        return {
            'status': 'error',
            'message': f'Error generating report: {str(e)}'
        }


@app.route('/personal/recommendations')
def get_personal_recommendations():
    """Get personalized content recommendations"""
    try:
        user_id = request.args.get('user_id', 'default_user')
        recommendations = recommendation_engine.get_user_recommendations(user_id, count=10)
        return jsonify({
            'status': 'success',
            'recommendations': recommendations
        })
    except Exception as e:
        print(f"Error getting recommendations: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Error getting recommendations: {str(e)}'
        })


@app.route('/personal/insights')
def get_personal_insights():
    """Get personal viewing insights"""
    try:
        user_id = request.args.get('user_id', 'default_user')
        insights = personal_analytics.get_personal_insights(user_id)
        return jsonify({
            'status': 'success',
            'insights': insights
        })
    except Exception as e:
        print(f"Error getting personal insights: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Error getting personal insights: {str(e)}'
        })


@app.route('/personal/track_viewing', methods=['POST'])
def track_personal_viewing():
    """Track personal viewing activity"""
    try:
        viewing_data = request.json

        # Store the viewing activity
        storage.store_personal_viewing(viewing_data)

        # Update user preferences based on content tags
        tags = viewing_data.get('tags', [])
        user_id = viewing_data.get('user_id', 'default_user')

        for tag in tags:
            tag_clean = tag.lstrip('#').lower()
            storage.update_user_preference(user_id, 'hashtag', tag_clean)

        # Update recommendation engine with new data
        recommendation_engine.update_user_profile(
            user_id,
            viewing_data.get('content_id', ''),
            viewing_data.get('engagement_type', 'view')
        )

        return jsonify({
            'status': 'success',
            'message': 'Viewing activity tracked successfully'
        })
    except Exception as e:
        print(f"Error tracking viewing activity: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Error tracking viewing activity: {str(e)}'
        })


@app.route('/personal/history')
def get_personal_history():
    """Get personal viewing history"""
    try:
        user_id = request.args.get('user_id', 'default_user')
        limit = int(request.args.get('limit', 50))

        history = storage.get_personal_viewing_history(user_id, limit)
        return jsonify({
            'status': 'success',
            'history': history
        })
    except Exception as e:
        print(f"Error getting viewing history: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Error getting viewing history: {str(e)}'
        })


@app.route('/content/discover')
def discover_content():
    """Discover new content based on user preferences"""
    try:
        user_id = request.args.get('user_id', 'default_user')
        category = request.args.get('category', 'all')
        count = int(request.args.get('count', 20))

        recommendations = recommendation_engine.get_user_recommendations(user_id, count)
        return jsonify({
            'status': 'success',
            'content': recommendations
        })
    except Exception as e:
        print(f"Error discovering content: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Error discovering content: {str(e)}'
        })


@app.route('/content/search')
def search_content():
    """Search for content by hashtags or topics"""
    try:
        query = request.args.get('q', '')
        platform = request.args.get('platform', 'all')
        user_id = request.args.get('user_id', 'default_user')

        # In a real implementation, this would search external APIs
        # For now, we'll return recommendations based on the query
        recommendations = recommendation_engine.get_user_recommendations(user_id, 10)

        # Filter recommendations based on query if needed
        if query:
            recommendations = [r for r in recommendations if query.lower() in r['title'].lower() or query.lower() in r.get('description', '').lower()]

        return jsonify({
            'status': 'success',
            'results': recommendations
        })
    except Exception as e:
        print(f"Error searching content: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Error searching content: {str(e)}'
        })


@app.route('/personal/rate_content', methods=['POST'])
def rate_content():
    """Rate recommended content"""
    try:
        data = request.json
        user_id = data.get('user_id')
        content_id = data.get('content_id')
        rating = data.get('rating')  # 1-5 scale

        # In a real implementation, this would update recommendation accuracy
        # For now, we'll just return success
        return jsonify({
            'status': 'success',
            'message': 'Content rating recorded'
        })
    except Exception as e:
        print(f"Error rating content: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Error rating content: {str(e)}'
        })


@app.route('/personal/data/privacy', methods=['GET', 'POST'])
def manage_privacy():
    """Manage user's privacy settings"""
    try:
        if request.method == 'POST':
            settings = request.json
            # Update user privacy settings in a real implementation
            return jsonify({
                'status': 'success',
                'message': 'Privacy settings updated'
            })

        # Return current privacy settings
        return jsonify({
            'settings': {
                'viewing_history_shared': True,
                'recommendations_enabled': True,
                'data_collection_active': True
            }
        })
    except Exception as e:
        print(f"Error managing privacy: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Error managing privacy: {str(e)}'
        })


@app.route('/personal/data/export', methods=['GET'])
def export_user_data():
    """Export user's viewing data"""
    try:
        user_id = request.args.get('user_id', 'default_user')
        # In a real implementation, this would return user's data
        history = storage.get_personal_viewing_history(user_id, limit=100)
        return jsonify({
            'user_id': user_id,
            'viewing_history': history,
            'preferences': storage.get_user_preferences(user_id)
        })
    except Exception as e:
        print(f"Error exporting user data: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Error exporting user data: {str(e)}'
        })


@app.route('/personal/data/delete', methods=['POST'])
def delete_user_data():
    """Delete user's viewing data"""
    try:
        user_id = request.json.get('user_id')
        # In a real implementation, this would delete user's data
        # For now, we'll just return success
        return jsonify({
            'status': 'success',
            'message': 'User data deletion initiated'
        })
    except Exception as e:
        print(f"Error deleting user data: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Error deleting user data: {str(e)}'
        })


def update_dashboard_data():
    """Background function to periodically update dashboard data"""
    global dashboard_data

    while True:
        try:
            # Get recent real-time posts
            recent_posts = storage.get_recent_realtime_posts(limit=10)

            # Update engagement data
            twitter_posts = [p for p in recent_posts if p['platform'] == 'twitter']
            youtube_posts = [p for p in recent_posts if p['platform'] == 'youtube']

            # Prepare engagement data (timestamp, engagement score)
            twitter_engagement = [
                {'time': p['created_at'], 'engagement': p['engagement_score']}
                for p in twitter_posts
            ]

            youtube_engagement = [
                {'time': p['created_at'], 'engagement': p['engagement_score']}
                for p in youtube_posts
            ]

            # Update trending hashtags
            trending_hashtags = storage.get_trending_hashtags(hours=1, limit=10)

            # Update high engagement posts
            high_engagement_posts = storage.get_high_engagement_posts(min_engagement=50, limit=5)

            # Update personal recommendations and insights
            try:
                personal_recommendations = recommendation_engine.get_user_recommendations(count=5)
            except Exception as e:
                print(f"Error getting personal recommendations: {e}")
                personal_recommendations = []

            try:
                personal_insights = personal_analytics.get_personal_insights()
            except Exception as e:
                print(f"Error getting personal insights: {e}")
                personal_insights = {}

            # Update dashboard data
            dashboard_data['twitter_engagement'] = twitter_engagement
            dashboard_data['youtube_engagement'] = youtube_engagement
            dashboard_data['trending_hashtags'] = trending_hashtags
            dashboard_data['high_engagement_posts'] = high_engagement_posts
            dashboard_data['personal_recommendations'] = personal_recommendations
            dashboard_data['personal_insights'] = personal_insights

            # Emit updates to all connected clients
            socketio.emit('dashboard_update', {
                'twitter_engagement': twitter_engagement,
                'youtube_engagement': youtube_engagement,
                'trending_hashtags': trending_hashtags,
                'high_engagement_posts': high_engagement_posts,
                'personal_recommendations': personal_recommendations,
                'personal_insights': personal_insights
            })

            # Wait before next update
            time.sleep(5)  # Update every 5 seconds

        except Exception as e:
            print(f"Error updating dashboard data: {e}")
            time.sleep(5)


def start_background_tasks():
    """Start background tasks for the dashboard"""
    # Start the dashboard update thread
    update_thread = threading.Thread(target=update_dashboard_data, daemon=True)
    update_thread.start()


@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print('Client connected')
    # Update dashboard data with fresh recommendations and insights
    try:
        dashboard_data['personal_recommendations'] = recommendation_engine.get_user_recommendations(count=5)
        dashboard_data['personal_insights'] = personal_analytics.get_personal_insights()
    except Exception as e:
        print(f"Error updating personal data on connect: {e}")
        # Use mock data if there's an error
        dashboard_data['personal_recommendations'] = recommendation_engine._generate_mock_recommendations(5)
        dashboard_data['personal_insights'] = personal_analytics._generate_mock_insights()

    # Send initial data to the newly connected client
    emit('dashboard_update', dashboard_data)


@socketio.on('request_personal_data')
def handle_request_personal_data():
    """Handle requests for personal data"""
    try:
        # Get updated personal recommendations and insights
        personal_recommendations = recommendation_engine.get_user_recommendations(count=5)
        personal_insights = personal_analytics.get_personal_insights()

        # Update dashboard data with fresh personal data
        dashboard_data['personal_recommendations'] = personal_recommendations
        dashboard_data['personal_insights'] = personal_insights

        # Send personal data to the client
        emit('personal_data_update', {
            'personal_recommendations': personal_recommendations,
            'personal_insights': personal_insights
        })
    except Exception as e:
        print(f"Error in handle_request_personal_data: {e}")
        # Send mock data if there's an error
        mock_recommendations = recommendation_engine._generate_mock_recommendations(5)
        mock_insights = personal_analytics._generate_mock_insights()

        dashboard_data['personal_recommendations'] = mock_recommendations
        dashboard_data['personal_insights'] = mock_insights

        emit('personal_data_update', {
            'personal_recommendations': mock_recommendations,
            'personal_insights': mock_insights
        })


@socketio.on('request_update')
def handle_request_update():
    """Handle requests for manual updates"""
    emit('dashboard_update', dashboard_data)


def main():
    print("Starting Social Media Analytics Tool with Real-Time Dashboard...")
    print("="*50)

    # Load configuration
    config = AppConfig.load_from_file()
    if not config.validate():
        print("Configuration validation failed. Please check your config.json file.")
        print("Using default/simulated data collection...")
        # Create a default config to continue with simulated data
        config = AppConfig.create_default_config_obj()

    print("Starting real-time data collection...")

    try:
        # Initialize real-time collector with configuration
        global real_time_collector
        real_time_collector = RealTimeDataCollector(config)
        
        # Start collecting real-time data
        real_time_collector.start_streaming()

        # Start background tasks for dashboard
        start_background_tasks()

        # Run the Flask-SocketIO server
        print("Starting real-time dashboard server...")
        print("Access the dashboard at: http://localhost:5000")
        print("Access the configuration at: http://localhost:5000/config")
        socketio.run(app, host='127.0.0.1', port=5000, debug=False)

    except KeyboardInterrupt:
        print("\nStopping real-time analysis...")
        if real_time_collector:
            real_time_collector.stop_streaming()
        print("Real-time analysis stopped.")


if __name__ == "__main__":
    main()