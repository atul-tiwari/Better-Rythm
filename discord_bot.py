import discord
from discord.ext import commands
import asyncio
import yt_dlp
import os
import json
from typing import Optional, List, Dict
from config import Config
from youtube_api import YouTubeMusicAPI

# Global bot instance
bot = None

class MusicBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.voice_states = True
        
        super().__init__(command_prefix='!', intents=intents)
        
        self.youtube_api = YouTubeMusicAPI()
        self.voice_client = None
        self.current_song = None
        self.queue = []
        self.queue_file = "queue.json"
        
        # YT-DLP options for audio only
        self.ytdl_opts = {
            'format': 'bestaudio/best',
            'extractaudio': True,
            'audioformat': 'mp3',
            'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
            'restrictfilenames': True,
            'noplaylist': True,
            'nocheckcertificate': True,
            'ignoreerrors': False,
            'logtostderr': False,
            'quiet': True,
            'no_warnings': True,
            'default_search': 'auto',
            'source_address': '0.0.0.0',
            'extract_flat': False,
        }
        
        self.ffmpeg_opts = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
            'options': '-vn',
            'executable': os.path.join(os.path.expanduser('~'), 'ffmpeg', 'ffmpeg.exe')
        }
        
        # Load queue from file
        self.load_queue()
    
    def load_queue(self):
        """Load queue from JSON file"""
        try:
            if os.path.exists(self.queue_file):
                with open(self.queue_file, 'r', encoding='utf-8') as f:
                    self.queue = json.load(f)
                print(f"Loaded {len(self.queue)} songs from queue file")
        except Exception as e:
            print(f"Error loading queue: {e}")
            self.queue = []
    
    def save_queue(self):
        """Save queue to JSON file"""
        try:
            with open(self.queue_file, 'w', encoding='utf-8') as f:
                json.dump(self.queue, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving queue: {e}")
    
    async def on_ready(self):
        print(f'{self.user} has connected to Discord!')
        print(f'Bot is in {len(self.guilds)} guilds')
    
    async def on_voice_state_update(self, member, before, after):
        """Handle voice state updates (user leaves/joins voice channel)"""
        if member == self.user:
            return
        
        # If bot is alone in voice channel, disconnect
        if self.voice_client and len(self.voice_client.channel.members) == 1:
            await self.voice_client.disconnect()
            self.voice_client = None
    
    async def join_voice_channel(self, ctx):
        """Join the voice channel of the user who sent the command"""
        if not ctx.author.voice:
            await ctx.send("You need to be in a voice channel to use this command!")
            return False
        
        channel = ctx.author.voice.channel
        
        if self.voice_client:
            if self.voice_client.channel == channel:
                return True
            else:
                await self.voice_client.move_to(channel)
        else:
            self.voice_client = await channel.connect()
        
        return True
    
    async def play_next_song(self, ctx):
        """Play the next song in the queue"""
        if not self.queue:
            await ctx.send("Queue is empty!")
            return
        
        song_data = self.queue.pop(0)
        self.current_song = song_data
        self.save_queue()
        
        try:
            # Download and play the song
            with yt_dlp.YoutubeDL(self.ytdl_opts) as ydl:
                info = ydl.extract_info(song_data['url'], download=False)
                url2 = info['url']
                
                source = discord.FFmpegPCMAudio(url2, **self.ffmpeg_opts)
                
                if self.voice_client:
                    self.voice_client.play(source, after=lambda e: asyncio.run_coroutine_threadsafe(
                        self.play_next_song(ctx), self.loop
                    ))
                    
                    embed = discord.Embed(
                        title="🎵 Now Playing",
                        description=f"**{song_data['title']}**\nby {song_data['artist']}",
                        color=0x00ff00
                    )
                    embed.set_thumbnail(url=song_data['thumbnail'])
                    embed.add_field(name="Duration", value=f"{song_data['duration']//60}:{song_data['duration']%60:02d}")
                    embed.add_field(name="Requested by", value=song_data['requested_by'])
                    
                    # Create control buttons
                    view = MusicControlView()
                    message = await ctx.send(embed=embed, view=view)
                    
                    # Disable buttons after 30 seconds
                    await asyncio.sleep(30)
                    view.disable_all_items()
                    await message.edit(view=view)
        
        except Exception as e:
            print(f"Error playing song: {e}")
            await ctx.send(f"Error playing song: {str(e)}")
            await self.play_next_song(ctx)

# Create bot instance
bot = MusicBot()

class MusicControlView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=30)
    
    @discord.ui.button(label="⏸️ Pause", style=discord.ButtonStyle.secondary)
    async def pause_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if bot.voice_client and bot.voice_client.is_playing():
            bot.voice_client.pause()
            await interaction.response.send_message("⏸️ Paused!", ephemeral=True)
        else:
            await interaction.response.send_message("Nothing is currently playing!", ephemeral=True)
    
    @discord.ui.button(label="▶️ Resume", style=discord.ButtonStyle.secondary)
    async def resume_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if bot.voice_client and bot.voice_client.is_paused():
            bot.voice_client.resume()
            await interaction.response.send_message("▶️ Resumed!", ephemeral=True)
        else:
            await interaction.response.send_message("Nothing is paused!", ephemeral=True)
    
    @discord.ui.button(label="⏭️ Skip", style=discord.ButtonStyle.primary)
    async def skip_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if bot.voice_client and bot.voice_client.is_playing():
            bot.voice_client.stop()
            await interaction.response.send_message("⏭️ Skipped!", ephemeral=True)
        else:
            await interaction.response.send_message("Nothing is currently playing!", ephemeral=True)
    
    @discord.ui.button(label="⏹️ Stop", style=discord.ButtonStyle.danger)
    async def stop_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if bot.voice_client:
            bot.voice_client.stop()
        bot.queue.clear()
        bot.current_song = None
        bot.save_queue()
        await interaction.response.send_message("⏹️ Stopped and cleared queue!", ephemeral=True)

class QueueView(discord.ui.View):
    def __init__(self, queue_data):
        super().__init__(timeout=60)
        self.queue_data = queue_data
    
    @discord.ui.button(label="🔄 Refresh", style=discord.ButtonStyle.secondary)
    async def refresh_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = create_queue_embed(bot.queue)
        await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(label="🗑️ Clear Queue", style=discord.ButtonStyle.danger)
    async def clear_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        bot.queue.clear()
        bot.save_queue()
        embed = create_queue_embed(bot.queue)
        await interaction.response.edit_message(embed=embed, view=self)

def create_queue_embed(queue):
    """Create queue embed"""
    embed = discord.Embed(title="🎵 Music Queue", color=0x00ff00)
    
    if not queue:
        embed.description = "Queue is empty!"
        return embed
    
    for i, song in enumerate(queue[:10], 1):  # Show first 10 songs
        embed.add_field(
            name=f"{i}. {song['title']}",
            value=f"by {song['artist']} | {song['duration']//60}:{song['duration']%60:02d}",
            inline=False
        )
    
    if len(queue) > 10:
        embed.set_footer(text=f"... and {len(queue) - 10} more songs")
    
    return embed

@bot.command(name='play', aliases=['p'])
async def play_song(ctx, *, query: str = None):
    """Play a song from YouTube Music or resume from queue"""
    if not await bot.join_voice_channel(ctx):
        return
    
    # If no query provided, try to play from queue
    if not query:
        if bot.queue:
            await bot.play_next_song(ctx)
            return
        else:
            await ctx.send("❌ No song specified and queue is empty! Use `!play song name` to add a song.")
            return
    
    # Show searching message
    search_msg = await ctx.send("🔍 Searching for song...")
    
    # Search for the song
    results = bot.youtube_api.search_song(query, max_results=1)
    
    if not results:
        await search_msg.edit(content="❌ No results found!")
        return
    
    song_data = results[0]
    
    # Check duration limit
    if song_data['duration'] > Config.MAX_SONG_DURATION:
        await search_msg.edit(content=f"❌ Song is too long! Maximum duration is {Config.MAX_SONG_DURATION//60} minutes.")
        return
    
    # Add to queue
    song_data['requested_by'] = ctx.author.display_name
    bot.queue.append(song_data)
    bot.save_queue()
    
    # Update search message
    embed = discord.Embed(
        title="✅ Added to Queue",
        description=f"**{song_data['title']}**\nby {song_data['artist']}",
        color=0x00ff00
    )
    embed.set_thumbnail(url=song_data['thumbnail'])
    embed.add_field(name="Position in queue", value=len(bot.queue))
    embed.add_field(name="Duration", value=f"{song_data['duration']//60}:{song_data['duration']%60:02d}")
    
    await search_msg.edit(content="", embed=embed)
    
    # Start playing if not already playing
    if not bot.voice_client.is_playing():
        await bot.play_next_song(ctx)

@bot.command(name='queue', aliases=['q'])
async def show_queue(ctx):
    """Show the current queue with interactive buttons"""
    embed = create_queue_embed(bot.queue)
    view = QueueView(bot.queue)
    await ctx.send(embed=embed, view=view)

@bot.command(name='skip', aliases=['s'])
async def skip_song(ctx):
    """Skip the current song"""
    if not bot.voice_client or not bot.voice_client.is_playing():
        await ctx.send("Nothing is currently playing!")
        return
    
    bot.voice_client.stop()
    await ctx.send("⏭️ Skipped current song!")

@bot.command(name='stop')
async def stop_music(ctx):
    """Stop the music and clear the queue"""
    if bot.voice_client:
        bot.voice_client.stop()
    
    bot.queue.clear()
    bot.current_song = None
    bot.save_queue()
    
    await ctx.send("⏹️ Stopped music and cleared queue!")

@bot.command(name='pause')
async def pause_music(ctx):
    """Pause the current song"""
    if not bot.voice_client or not bot.voice_client.is_playing():
        await ctx.send("Nothing is currently playing!")
        return
    
    bot.voice_client.pause()
    await ctx.send("⏸️ Paused!")

@bot.command(name='resume')
async def resume_music(ctx):
    """Resume the paused song"""
    if not bot.voice_client or bot.voice_client.is_playing():
        await ctx.send("Nothing is paused!")
        return
    
    bot.voice_client.resume()
    await ctx.send("▶️ Resumed!")

@bot.command(name='remove', aliases=['rm'])
async def remove_song(ctx, position: int):
    """Remove a song from the queue by position"""
    if not bot.queue:
        await ctx.send("Queue is empty!")
        return
    
    if position < 1 or position > len(bot.queue):
        await ctx.send(f"Invalid position! Queue has {len(bot.queue)} songs.")
        return
    
    removed_song = bot.queue.pop(position - 1)
    bot.save_queue()
    
    embed = discord.Embed(
        title="🗑️ Song Removed",
        description=f"**{removed_song['title']}**\nby {removed_song['artist']}",
        color=0xff0000
    )
    await ctx.send(embed=embed)

@bot.command(name='move', aliases=['mv'])
async def move_song(ctx, from_pos: int, to_pos: int):
    """Move a song in the queue"""
    if not bot.queue:
        await ctx.send("Queue is empty!")
        return
    
    if from_pos < 1 or from_pos > len(bot.queue) or to_pos < 1 or to_pos > len(bot.queue):
        await ctx.send(f"Invalid positions! Queue has {len(bot.queue)} songs.")
        return
    
    # Move the song
    song = bot.queue.pop(from_pos - 1)
    bot.queue.insert(to_pos - 1, song)
    bot.save_queue()
    
    embed = discord.Embed(
        title="🔄 Song Moved",
        description=f"**{song['title']}**\nMoved from position {from_pos} to {to_pos}",
        color=0x00ff00
    )
    await ctx.send(embed=embed)

@bot.command(name='shuffle')
async def shuffle_queue(ctx):
    """Shuffle the queue"""
    if len(bot.queue) < 2:
        await ctx.send("Need at least 2 songs to shuffle!")
        return
    
    import random
    random.shuffle(bot.queue)
    bot.save_queue()
    
    await ctx.send("🔀 Queue shuffled!")

@bot.command(name='nowplaying', aliases=['np'])
async def now_playing(ctx):
    """Show currently playing song"""
    if not bot.current_song:
        await ctx.send("Nothing is currently playing!")
        return
    
    embed = discord.Embed(
        title="🎵 Now Playing",
        description=f"**{bot.current_song['title']}**\nby {bot.current_song['artist']}",
        color=0x00ff00
    )
    embed.set_thumbnail(url=bot.current_song['thumbnail'])
    embed.add_field(name="Duration", value=f"{bot.current_song['duration']//60}:{bot.current_song['duration']%60:02d}")
    embed.add_field(name="Requested by", value=bot.current_song['requested_by'])
    
    view = MusicControlView()
    await ctx.send(embed=embed, view=view)

@bot.command(name='connect', aliases=['join'])
async def connect_bot(ctx):
    """Connect the bot to your voice channel"""
    if await bot.join_voice_channel(ctx):
        await ctx.send("🎵 Connected to voice channel! Use `!play song name` to start playing music!")
    else:
        await ctx.send("❌ Could not connect to voice channel!")

@bot.command(name='disconnect', aliases=['dc'])
async def disconnect_bot(ctx):
    """Disconnect the bot from voice channel"""
    if bot.voice_client:
        await bot.voice_client.disconnect()
        bot.voice_client = None
        await ctx.send("👋 Disconnected from voice channel!")
    else:
        await ctx.send("I'm not connected to any voice channel!")

@bot.command(name='help_music')
async def help_command(ctx):
    """Show help information"""
    embed = discord.Embed(
        title="🎵 Discord Music Bot Commands",
        description="Here are all the available commands:",
        color=0x00ff00
    )
    
    commands = [
        ("!play <song>", "Play a song or add to queue"),
        ("!queue", "Show current queue with buttons"),
        ("!skip", "Skip current song"),
        ("!stop", "Stop music and clear queue"),
        ("!pause", "Pause current song"),
        ("!resume", "Resume paused song"),
        ("!remove <position>", "Remove song from queue"),
        ("!move <from> <to>", "Move song in queue"),
        ("!shuffle", "Shuffle the queue"),
        ("!nowplaying", "Show currently playing song"),
        ("!connect", "Connect bot to voice channel"),
        ("!disconnect", "Disconnect bot from voice channel"),
        ("!help_music", "Show this help message")
    ]
    
    for cmd, desc in commands:
        embed.add_field(name=cmd, value=desc, inline=False)
    
    await ctx.send(embed=embed)