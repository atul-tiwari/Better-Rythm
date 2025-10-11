# Discord Music Bot

A feature-rich Discord music bot with interactive buttons, advanced queue management, and YouTube Music integration. Built with Discord.py and designed for seamless music streaming in Discord voice channels.

## 🎵 Core Features

### **Interactive Music Control**
- **Smart Playback**: Automatic queue management with seamless song transitions
- **Interactive Buttons**: Pause, Resume, Skip, and Stop buttons appear during playback
- **Rich Embeds**: Beautiful song information with thumbnails and metadata
- **Auto-disconnect**: Bot automatically leaves when alone in voice channel

### **Advanced Queue Management**
- **Persistent Queue**: Songs saved to JSON file, survive bot restarts
- **Queue Manipulation**: Add, remove, reorder, and shuffle songs
- **Position Control**: Move songs to specific positions in queue
- **Queue Display**: Interactive queue view with refresh and clear buttons

### **YouTube Music Integration**
- **Ad-free Streaming**: High-quality music from YouTube Music API
- **Smart Search**: Intelligent song search with duration validation
- **Metadata Rich**: Full song information including artist, duration, and thumbnails
- **Duration Limits**: Configurable maximum song length protection

## 📁 Project Structure

```
discord-music-bot/
├── main.py                 # Application entry point
├── discord_bot.py          # Core Discord bot implementation
├── youtube_api.py          # YouTube Music API integration
├── config.py               # Configuration management
├── requirements.txt        # Python dependencies
├── config.env.example     # Environment variables template
├── .gitignore             # Git ignore rules
└── README.md              # This documentation
```

## 🔧 File Descriptions

### **Core Application Files**

#### `main.py`
- **Purpose**: Application entry point and startup logic
- **Functionality**: 
  - Validates configuration
  - Starts the Discord bot
  - Handles startup errors gracefully
- **Dependencies**: `discord_bot`, `config`

#### `discord_bot.py`
- **Purpose**: Main Discord bot implementation with all music functionality
- **Key Classes**:
  - `MusicBot`: Main bot class extending `commands.Bot`
  - `MusicControlView`: Interactive buttons for music control
  - `QueueView`: Interactive buttons for queue management
- **Key Methods**:
  - `play_next_song()`: Handles song playback and queue progression
  - `join_voice_channel()`: Manages voice channel connections
  - `load_queue()` / `save_queue()`: JSON-based queue persistence
- **Commands**: 13 Discord commands for complete music control

#### `youtube_api.py`
- **Purpose**: YouTube Music API integration and song search
- **Key Class**: `YouTubeMusicAPI`
- **Key Methods**:
  - `search_song()`: Search for songs with metadata
  - `_get_video_duration()`: Extract song duration
  - `_parse_duration()`: Convert ISO duration to seconds
  - `extract_video_id()`: Parse YouTube URLs
- **Features**: Error handling, duration validation, metadata extraction

#### `config.py`
- **Purpose**: Centralized configuration management
- **Key Class**: `Config`
- **Configuration Areas**:
  - Discord bot settings (token, guild ID)
  - YouTube API configuration
  - Bot behavior settings (queue size, song duration limits)
- **Validation**: `validate()` method ensures required settings

### **Support Files**

#### `requirements.txt`
- **Purpose**: Python package dependencies
- **Core Dependencies**:
  - `discord.py`: Discord API wrapper
  - `yt-dlp`: YouTube video/audio extraction
  - `python-dotenv`: Environment variable management
  - `requests`: HTTP requests for API calls
  - `PyNaCl`: Audio encryption for Discord


#### `config.env.example`
- **Purpose**: Template for environment configuration
- **Contains**: All required environment variables with examples
- **Security**: Safe template without actual credentials

## 🎮 Discord Commands

### **Music Control Commands**
- `!play <song>` - Play song or add to queue
- `!skip` - Skip current song
- `!pause` - Pause playback
- `!resume` - Resume playback
- `!stop` - Stop music and clear queue
- `!nowplaying` - Show current song with controls

### **Queue Management Commands**
- `!queue` - Display queue with interactive buttons
- `!remove <position>` - Remove song from specific position
- `!move <from> <to>` - Move song to different position
- `!shuffle` - Randomize queue order

### **Connection Commands**
- `!connect` - Join voice channel
- `!disconnect` - Leave voice channel
- `!help_music` - Show all available commands

## 🔄 Bot Workflow

### **Song Playback Process**
1. **Search**: User requests song via `!play`
2. **Validation**: Check duration limits and API availability
3. **Queue Addition**: Add song to persistent JSON queue
4. **Playback**: Extract audio stream using yt-dlp
5. **Control**: Display interactive buttons for user control
6. **Progression**: Automatically play next song when current ends

### **Queue Management Process**
1. **Persistence**: Queue automatically saved to `queue.json`
2. **Manipulation**: Users can reorder, remove, or shuffle songs
3. **Display**: Rich embeds show queue with metadata
4. **Interactivity**: Buttons provide instant queue control

### **Error Handling**
- **API Failures**: Graceful fallback for YouTube API issues
- **Network Issues**: Automatic reconnection for audio streams
- **Permission Errors**: Clear error messages for Discord permissions
- **File Errors**: Safe handling of queue file operations

## 🎯 Key Features Explained

### **Interactive Buttons**
- **MusicControlView**: Appears during song playback
  - Pause/Resume toggle
  - Skip to next song
  - Stop and clear queue
- **QueueView**: Appears in queue display
  - Refresh queue display
  - Clear entire queue
- **Ephemeral Responses**: Button interactions are private to user

### **Queue Persistence**
- **JSON Storage**: Queue saved to `queue.json` file
- **Auto-save**: Queue updated after every modification
- **Restart Survival**: Songs remain in queue after bot restart
- **Error Recovery**: Graceful handling of corrupted queue files

### **Smart Search**
- **YouTube Music API**: Official API for high-quality results
- **Metadata Extraction**: Full song information including duration
- **Duration Validation**: Automatic filtering of overly long songs
- **Error Handling**: Fallback for API failures

### **Rich User Experience**
- **Beautiful Embeds**: Song information with thumbnails and metadata
- **Real-time Updates**: Instant feedback for all user actions
- **Intuitive Commands**: Easy-to-remember command structure
- **Help System**: Built-in help command with all available functions

## 🚀 Technical Architecture

### **Async Programming**
- Built on Discord.py's async framework
- Non-blocking audio playback
- Concurrent queue management
- Efficient resource utilization

### **Modular Design**
- Separation of concerns across files
- Reusable components (views, embeds)
- Clean API integration
- Easy maintenance and extension

### **Error Resilience**
- Comprehensive error handling
- Graceful degradation
- User-friendly error messages
- Automatic recovery mechanisms

This Discord Music Bot provides a complete, professional-grade music streaming solution with modern Discord features and robust functionality.