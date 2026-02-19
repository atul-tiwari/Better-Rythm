import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Discord Configuration
    DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
    DISCORD_GUILD_ID = int(os.getenv('DISCORD_GUILD_ID', 0))
    
    # YouTube API Configuration
    YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')
    
    # Bot Settings
    MAX_QUEUE_SIZE = int(os.getenv('MAX_QUEUE_SIZE', 50))
    MAX_SONG_DURATION = int(os.getenv('MAX_SONG_DURATION', 600))
    DEFAULT_VOLUME = float(os.getenv('DEFAULT_VOLUME', 0.5))
    # Optional: path to ffmpeg directory or to ffmpeg.exe (so yt-dlp and the bot can find ffmpeg/ffprobe)
    FFMPEG_LOCATION = os.getenv('FFMPEG_LOCATION', '').strip() or None
    
    @staticmethod
    def validate():
        """Validate that all required configuration is present"""
        required_vars = ['DISCORD_TOKEN', 'YOUTUBE_API_KEY']
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
        
        return True
