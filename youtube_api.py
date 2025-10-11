import requests
import re
import json
from typing import Dict, List, Optional
from config import Config

class YouTubeMusicAPI:
    def __init__(self):
        self.api_key = Config.YOUTUBE_API_KEY
        self.base_url = "https://www.googleapis.com/youtube/v3"
        
    def search_song(self, query: str, max_results: int = 5) -> List[Dict]:
        """Search for songs on YouTube Music"""
        try:
            # Use YouTube Data API v3 for search
            search_url = f"{self.base_url}/search"
            params = {
                'part': 'snippet',
                'q': query,
                'type': 'video',
                'maxResults': max_results,
                'key': self.api_key,
                'videoCategoryId': '10'  # Music category
            }
            
            response = requests.get(search_url, params=params)
            response.raise_for_status()
            
            results = []
            for item in response.json().get('items', []):
                video_id = item['id']['videoId']
                snippet = item['snippet']
                
                # Extract duration from video details
                duration = self._get_video_duration(video_id)
                
                results.append({
                    'id': video_id,
                    'title': snippet['title'],
                    'artist': snippet['channelTitle'],
                    'thumbnail': snippet['thumbnails']['medium']['url'],
                    'duration': duration,
                    'url': f"https://www.youtube.com/watch?v={video_id}"
                })
            
            return results
            
        except Exception as e:
            print(f"Error searching for song: {e}")
            return []
    
    def _get_video_duration(self, video_id: str) -> Optional[int]:
        """Get video duration in seconds"""
        try:
            url = f"{self.base_url}/videos"
            params = {
                'part': 'contentDetails',
                'id': video_id,
                'key': self.api_key
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            items = response.json().get('items', [])
            if items:
                duration_str = items[0]['contentDetails']['duration']
                return self._parse_duration(duration_str)
            
            return None
            
        except Exception as e:
            print(f"Error getting video duration: {e}")
            return None
    
    def _parse_duration(self, duration_str: str) -> int:
        """Parse ISO 8601 duration format to seconds"""
        # Remove PT prefix
        duration_str = duration_str.replace('PT', '')
        
        # Parse hours, minutes, seconds
        hours = 0
        minutes = 0
        seconds = 0
        
        if 'H' in duration_str:
            hours = int(duration_str.split('H')[0])
            duration_str = duration_str.split('H')[1]
        
        if 'M' in duration_str:
            minutes = int(duration_str.split('M')[0])
            duration_str = duration_str.split('M')[1]
        
        if 'S' in duration_str:
            seconds = int(duration_str.replace('S', ''))
        
        return hours * 3600 + minutes * 60 + seconds
    
    def get_video_info(self, video_id: str) -> Optional[Dict]:
        """Get detailed information about a specific video"""
        try:
            url = f"{self.base_url}/videos"
            params = {
                'part': 'snippet,contentDetails',
                'id': video_id,
                'key': self.api_key
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            items = response.json().get('items', [])
            if items:
                item = items[0]
                snippet = item['snippet']
                duration = self._parse_duration(item['contentDetails']['duration'])
                
                return {
                    'id': video_id,
                    'title': snippet['title'],
                    'artist': snippet['channelTitle'],
                    'thumbnail': snippet['thumbnails']['medium']['url'],
                    'duration': duration,
                    'url': f"https://www.youtube.com/watch?v={video_id}"
                }
            
            return None
            
        except Exception as e:
            print(f"Error getting video info: {e}")
            return None
    
    def extract_video_id(self, url: str) -> Optional[str]:
        """Extract video ID from YouTube URL"""
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\n?#]+)',
            r'youtube\.com\/watch\?.*v=([^&\n?#]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None
