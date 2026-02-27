import requests
import re
import json
from typing import Dict, List, Optional
from config import Config
from ytmusicapi import YTMusic

class YouTubeMusicAPI:
    def __init__(self):
        self.api_key = Config.YOUTUBE_API_KEY
        self.base_url = "https://www.googleapis.com/youtube/v3"
        self.ytmusic = YTMusic()
        
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
    
    _TITLE_NOISE = re.compile(
        r'[\(\[]\s*(?:Official\s*(?:Music\s*)?Video|Official\s*Audio|'
        r'Lyric(?:s)?\s*Video|Audio\s*(?:Only)?|HD|HQ|4K|MV|M/V|'
        r'Visuali[sz]er|Live|Remix|Extended|Explicit|Clean)\s*[\)\]]',
        re.IGNORECASE,
    )

    @staticmethod
    def _clean_title(title: str) -> str:
        """Strip common noise phrases from a video title for a cleaner search query."""
        title = YouTubeMusicAPI._TITLE_NOISE.sub('', title)
        title = re.sub(r'\s{2,}', ' ', title).strip()
        return title

    @staticmethod
    def _clean_artist(artist: str) -> str:
        """Strip VEVO / '- Topic' suffixes from channel names."""
        artist = re.sub(r'\s*[-–]\s*Topic$', '', artist, flags=re.IGNORECASE)
        artist = re.sub(r'VEVO$', '', artist, flags=re.IGNORECASE)
        return artist.strip()

    @staticmethod
    def _parse_length(length_str: str) -> Optional[int]:
        """Parse a 'M:SS' or 'H:MM:SS' length string into total seconds."""
        if not length_str:
            return None
        parts = length_str.split(':')
        try:
            parts = [int(p) for p in parts]
        except ValueError:
            return None
        if len(parts) == 2:
            return parts[0] * 60 + parts[1]
        if len(parts) == 3:
            return parts[0] * 3600 + parts[1] * 60 + parts[2]
        return None

    def get_related_songs(self, video_id: str, max_results: int = 5,
                          title: str = None, artist: str = None) -> List[Dict]:
        """Get similar songs using YouTube Music's radio algorithm.

        Falls back to keyword search if ytmusicapi fails.
        """
        try:
            result = self.ytmusic.get_watch_playlist(videoId=video_id, limit=max_results + 5)
            tracks = result.get("tracks", [])

            results = []
            for t in tracks:
                vid = t.get("videoId")
                if not vid or vid == video_id:
                    continue
                duration = self._parse_length(t.get("length"))
                if duration is not None and duration > Config.MAX_SONG_DURATION:
                    continue
                thumbnails = t.get("thumbnail") or []
                thumb_url = thumbnails[0]["url"] if thumbnails else ""
                artists = ", ".join(a["name"] for a in (t.get("artists") or []))
                results.append({
                    'id': vid,
                    'title': t.get("title", ""),
                    'artist': artists,
                    'thumbnail': thumb_url,
                    'duration': duration,
                    'url': f"https://www.youtube.com/watch?v={vid}"
                })
                if len(results) >= max_results:
                    break

            if results:
                return results
        except Exception as e:
            print(f"ytmusicapi radio failed, falling back to keyword search: {e}")

        return self._get_related_songs_fallback(video_id, max_results, title, artist)

    def _get_related_songs_fallback(self, video_id: str, max_results: int = 5,
                                    title: str = None, artist: str = None) -> List[Dict]:
        """Fallback: keyword search via YouTube Data API."""
        try:
            if not title:
                info = self.get_video_info(video_id)
                if not info:
                    return []
                title = info['title']
                artist = info.get('artist', '')

            query = self._clean_title(title)
            if artist:
                clean_artist = self._clean_artist(artist)
                if clean_artist:
                    query = f"{clean_artist} {query}"

            search_url = f"{self.base_url}/search"
            params = {
                'part': 'snippet',
                'q': query,
                'type': 'video',
                'maxResults': max_results + 5,
                'key': self.api_key,
                'videoCategoryId': '10',
            }
            response = requests.get(search_url, params=params)
            response.raise_for_status()

            results = []
            for item in response.json().get('items', []):
                vid = item['id'].get('videoId')
                if not vid or vid == video_id:
                    continue
                snippet = item['snippet']
                duration = self._get_video_duration(vid)
                if duration is None or duration > Config.MAX_SONG_DURATION:
                    continue
                results.append({
                    'id': vid,
                    'title': snippet['title'],
                    'artist': snippet['channelTitle'],
                    'thumbnail': snippet['thumbnails']['medium']['url'],
                    'duration': duration,
                    'url': f"https://www.youtube.com/watch?v={vid}"
                })
                if len(results) >= max_results:
                    break
            return results
        except Exception as e:
            print(f"Error getting related songs: {e}")
            return []

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
