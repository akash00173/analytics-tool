// Content Tracker for Social Media Viewing Activity
// This script would be part of a browser extension

class ContentTracker {
    constructor(apiEndpoint, apiKey) {
        this.apiEndpoint = apiEndpoint || '/personal/track_viewing';
        this.apiKey = apiKey;
        this.trackedContent = new Set();
        this.startTime = null;
        this.currentContent = null;
        
        this.init();
    }
    
    init() {
        // Start tracking when page loads
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.setupTracking());
        } else {
            this.setupTracking();
        }
    }
    
    setupTracking() {
        // Track YouTube videos
        if (window.location.hostname.includes('youtube.com')) {
            this.trackYouTube();
        }
        // Track Twitter content
        else if (window.location.hostname.includes('twitter.com')) {
            this.trackTwitter();
        }
    }
    
    trackYouTube() {
        // Monitor YouTube video player
        const self = this;
        
        // Track when video starts playing
        function checkForVideo() {
            const video = document.querySelector('video');
            if (video && !self.currentContent) {
                const videoId = self.extractYouTubeId(window.location.href);
                if (videoId && !self.trackedContent.has(videoId)) {
                    self.startTracking(videoId, 'youtube');
                }
            }
        }
        
        // Check periodically for video element
        setInterval(checkForVideo, 1000);
        
        // Also check when page changes (for single page apps)
        let currentUrl = window.location.href;
        setInterval(() => {
            if (currentUrl !== window.location.href) {
                currentUrl = window.location.href;
                setTimeout(checkForVideo, 2000); // Wait for page to load
            }
        }, 500);
    }
    
    trackTwitter() {
        const self = this;
        
        // Track when user views tweets
        function observeTweets() {
            const tweets = document.querySelectorAll('article[data-testid="tweet"]');
            tweets.forEach(tweet => {
                const tweetId = tweet.getAttribute('data-tweet-id') || self.extractTweetId(tweet.innerHTML);
                if (tweetId && !self.trackedContent.has(tweetId)) {
                    // Track tweet when it's in viewport for a certain time
                    self.observeElementVisibility(tweet, () => {
                        self.startTracking(tweetId, 'twitter');
                    });
                }
            });
        }
        
        // Observe for new tweets being loaded
        const observer = new MutationObserver(() => {
            observeTweets();
        });
        
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
        
        // Initial check
        setTimeout(observeTweets, 2000);
    }
    
    extractYouTubeId(url) {
        const regExp = /^.*(youtu.be\/|v\/|u\/\w\/|embed\/|watch\?v=|&v=)([^#&?]*).*/;
        const match = url.match(regExp);
        return (match && match[2].length === 11) ? match[2] : null;
    }
    
    extractTweetId(content) {
        // Simple extraction - in real implementation would be more robust
        const tweetIdMatch = content.match(/status\/(\d+)/);
        return tweetIdMatch ? tweetIdMatch[1] : null;
    }
    
    observeElementVisibility(element, callback) {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    // Wait 3 seconds to ensure user is actually viewing
                    setTimeout(() => {
                        if (entry.isIntersecting) {
                            callback();
                        }
                    }, 3000);
                }
            });
        }, { threshold: 0.5 }); // Element is 50% visible
        
        observer.observe(element);
    }
    
    startTracking(contentId, platform) {
        if (this.currentContent) {
            this.stopTracking();
        }
        
        this.currentContent = {
            id: contentId,
            platform: platform,
            startTime: Date.now()
        };
        
        this.trackedContent.add(contentId);
        
        console.log(`Started tracking ${platform} content: ${contentId}`);
        
        // Set up interval to periodically update tracking
        this.trackingInterval = setInterval(() => {
            this.updateTracking();
        }, 30000); // Update every 30 seconds
    }
    
    stopTracking() {
        if (this.currentContent) {
            const duration = Math.floor((Date.now() - this.currentContent.startTime) / 1000);
            
            this.sendTrackingData({
                platform: this.currentContent.platform,
                content_id: this.currentContent.id,
                watch_duration: duration,
                engagement_type: 'view',
                user_id: 'current_user' // Would be replaced with actual user ID
            });
            
            console.log(`Stopped tracking ${this.currentContent.platform} content: ${this.currentContent.id}, duration: ${duration}s`);
            
            if (this.trackingInterval) {
                clearInterval(this.trackingInterval);
            }
            
            this.currentContent = null;
        }
    }
    
    updateTracking() {
        if (this.currentContent) {
            const duration = Math.floor((Date.now() - this.currentContent.startTime) / 1000);
            
            // Send periodic update without stopping tracking
            this.sendTrackingData({
                platform: this.currentContent.platform,
                content_id: this.currentContent.id,
                watch_duration: duration,
                engagement_type: 'view',
                user_id: 'current_user'
            }, true); // isUpdate flag
        }
    }
    
    async sendTrackingData(data, isUpdate = false) {
        try {
            // Get content details if possible
            if (data.platform === 'youtube') {
                data.content_title = this.getCurrentYouTubeTitle();
                data.content_url = window.location.href;
                data.tags = this.getCurrentYouTubeTags();
            } else if (data.platform === 'twitter') {
                data.content_title = this.getCurrentTwitterContent();
                data.content_url = window.location.href;
            }
            
            const response = await fetch(this.apiEndpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.apiKey}`,
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify(data)
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const result = await response.json();
            console.log('Tracking data sent successfully:', result);
            
        } catch (error) {
            console.error('Error sending tracking data:', error);
        }
    }
    
    getCurrentYouTubeTitle() {
        const titleElement = document.querySelector('h1.ytd-watch-metadata #video-title');
        return titleElement ? titleElement.textContent.trim() : '';
    }
    
    getCurrentYouTubeTags() {
        // YouTube doesn't easily expose tags, but we could extract from description or metadata
        const description = document.querySelector('#description');
        if (description) {
            // Extract hashtags from description
            const hashtags = description.textContent.match(/#\w+/g) || [];
            return hashtags;
        }
        return [];
    }
    
    getCurrentTwitterContent() {
        // Extract content from current tweet
        const tweetElement = document.querySelector(`article[data-tweet-id="${this.currentContent.id}"]`) ||
                           document.querySelector(`[data-testid="tweet"] a[href*="${this.currentContent.id}"]`)?.closest('article');
        
        if (tweetElement) {
            const textElement = tweetElement.querySelector('div[data-testid="tweetText"]');
            return textElement ? textElement.textContent.trim() : '';
        }
        return '';
    }
}

// Initialize the tracker when script loads
// This would be configured with your API endpoint and key
document.addEventListener('DOMContentLoaded', function() {
    // Initialize with your server endpoint and API key
    // These would be configured by the extension
    const tracker = new ContentTracker(
        'http://localhost:5000/personal/track_viewing', // Replace with your server endpoint
        'your_browser_extension_api_key' // Replace with actual API key
    );
});

// Export for use in browser extension
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ContentTracker;
}