import os
from discord_bot import bot
from config import Config

def main():
    """Main function to start Discord bot"""
    try:
        # Validate configuration
        Config.validate()
        
        print("Starting Discord Music Bot...")
        print("Bot will be available in Discord!")
        
        # Run the bot
        bot.run(Config.DISCORD_TOKEN)
        
    except ValueError as e:
        print(f"Configuration error: {e}")
        print("Please check your .env file and ensure all required variables are set.")
    except Exception as e:
        print(f"Error starting application: {e}")

if __name__ == "__main__":
    main()
