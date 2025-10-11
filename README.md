`# Discord Music Bot with YouTube Music API

A comprehensive Discord music bot that uses YouTube Music API for ad-free music streaming, with a Flask web interface for queue management.

## Features

- 🎵 **Ad-free Music Streaming**: Uses YouTube Music API for high-quality, ad-free music
- 🎛️ **Web Interface**: Beautiful Flask web app for queue management
- 🔄 **Real-time Updates**: WebSocket integration for live queue updates
- 📱 **Responsive Design**: Modern, mobile-friendly web interface
- 🎚️ **Queue Management**: Add, remove, reorder songs in the queue
- 🔍 **Smart Search**: Search and add songs directly from the web interface
- 📊 **Status Monitoring**: Real-time bot status and current song display

## Prerequisites

- Python 3.8 or higher
- Discord Bot Token
- YouTube Data API v3 Key
- FFmpeg installed on your system

## Installation

1. **Clone or download this project**
   ```bash
   git clone <repository-url>
   cd discord-music-bot
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install FFmpeg**
   - **Windows**: Download from https://ffmpeg.org/download.html and add to PATH
   - **macOS**: `brew install ffmpeg`
   - **Linux**: `sudo apt install ffmpeg`

4. **Set up environment variables**
   - Copy `config.env.example` to `.env`
   - Fill in your configuration values:
   ```env
   DISCORD_TOKEN=your_discord_bot_token_here
   DISCORD_GUILD_ID=your_guild_id_here
   YOUTUBE_API_KEY=your_youtube_api_key_here
   FLASK_SECRET_KEY=your_secret_key_here
   ```

## Discord Bot Setup

1. **Create a Discord Application**
   - Go to https://discord.com/developers/applications
   - Click "New Application"
   - Give it a name and create

2. **Create a Bot**
   - Go to the "Bot" section
   - Click "Add Bot"
   - Copy the bot token and add it to your `.env` file

3. **Set Bot Permissions**
   - Go to "OAuth2" > "URL Generator"
   - Select "bot" scope
   - Select these permissions:
     - Send Messages
     - Use Slash Commands
     - Connect
     - Speak
     - Use Voice Activity
   - Copy the generated URL and invite the bot to your server

## YouTube API Setup

1. **Create a Google Cloud Project**
   - Go to https://console.cloud.google.com/
   - Create a new project or select existing one

2. **Enable YouTube Data API v3**
   - Go to "APIs & Services" > "Library"
   - Search for "YouTube Data API v3"
   - Click "Enable"

3. **Create API Key**
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "API Key"
   - Copy the API key and add it to your `.env` file

## Usage

### Starting the Application

```bash
python main.py
```

The application will start both the Discord bot and Flask web interface.

### Discord Commands

- `!play <song name>` - Play a song
- `!queue` - Show current queue
- `!skip` - Skip current song
- `!pause` - Pause music
- `!resume` - Resume music
- `!stop` - Stop music and clear queue
- `!disconnect` - Disconnect bot from voice channel

### Web Interface

Access the web interface at `http://localhost:5000` (or your configured host/port).

**Features:**
- Search for songs and add them to the queue
- View and manage the current queue
- Reorder songs by moving them up/down
- Remove individual songs or clear the entire queue
- Monitor bot status and currently playing song

## Configuration Options

Edit your `.env` file to customize:

- `MAX_QUEUE_SIZE`: Maximum number of songs in queue (default: 50)
- `MAX_SONG_DURATION`: Maximum song duration in seconds (default: 600)
- `DEFAULT_VOLUME`: Default volume level (default: 0.5)
- `FLASK_HOST`: Flask app host (default: 0.0.0.0)
- `FLASK_PORT`: Flask app port (default: 5000)

## File Structure

```
discord-music-bot/
├── main.py                 # Main application entry point
├── discord_bot.py          # Discord bot implementation
├── flask_app.py            # Flask web application
├── youtube_api.py          # YouTube Music API integration
├── models.py               # Database models
├── config.py               # Configuration management
├── requirements.txt        # Python dependencies
├── config.env.example     # Environment variables template
├── templates/
│   └── index.html         # Web interface template
├── static/
│   └── app.js            # Web interface JavaScript
└── README.md             # This file
```

## Troubleshooting

### Common Issues

1. **Bot doesn't join voice channel**
   - Ensure the bot has proper permissions
   - Check that you're in a voice channel when using commands

2. **Music doesn't play**
   - Verify FFmpeg is installed and in PATH
   - Check YouTube API key is valid
   - Ensure internet connection is stable

3. **Web interface not accessible**
   - Check firewall settings
   - Verify Flask host/port configuration
   - Ensure no other application is using the port

4. **Database errors**
   - Delete `music_bot.db` to reset the database
   - Check file permissions

### Logs

The application will output logs to the console. Check for error messages if something isn't working.

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is open source and available under the MIT License.
