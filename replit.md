# Meat Bro Discord Bot

## Overview
This is a Discord bot named "Meat Bro" that embodies the persona of a confident, brash disciple of the "Raw Meat Boyz" movement. The bot uses Google's Gemini LLM API to generate responses and interacts with Discord users in a casual, slang-filled manner.

## Project Status
✅ **Setup Complete** - Discord bot ready to deploy and run 24/7

## Recent Changes
- **2025-10-20**: Configured deployment settings for production
  - Set up VM deployment configuration for always-on operation
  - Bot is now ready to be published and run 24/7 with dedicated resources
- **2025-10-17**: Refactored project structure into modular files
  - Split single main.py into organized components: bot.py, config.py, llm.py, utils.py
  - Updated workflow to run bot.py instead of main.py
  - Improved code organization and maintainability
- **2025-10-16**: Made bot reply logic much more conservative
  - Completely rewrote decision prompt to default to NO unless explicitly engaged
  - Added automatic reply for direct replies and mentions (bypasses AI check)
  - Bot now only joins conversations when directly addressed or mentioned
  - Explicitly prevents bot from interrupting conversations between other users
  - Will no longer respond just because topic is gym/fitness related
- **2025-10-16**: Improved mention behavior for Baggins and Snazzy Daddy
  - Removed random name-dropping quirk that forced unnecessary mentions
  - Bot now detects when talking directly to Baggins or Snazzy Daddy
  - Prevents mentioning users to themselves while still mentioning them when contextually relevant
  - Added `current_user_id` parameter to `get_llm_response()` for user recognition
- **2025-10-16**: Added AI-powered response decision system
  - Bot now uses AI to intelligently decide whether to respond to messages
  - Considers conversation context, message content, and recent interactions
  - Prevents spam by avoiding responses to casual chatter that doesn't need bot input
  - New `should_bot_reply()` function analyzes each message before responding
- **2025-10-15**: Initial Replit environment setup
  - Migrated hardcoded API keys to environment variables for security
  - Created requirements.txt for dependency management
  - Set up Discord Bot workflow
  - Added .gitignore for Python and sensitive files
  - Added error handling for missing API keys

## Features
- **AI-Powered Response Decision**: Uses AI to intelligently decide when to respond based on message context, conversation history, and relevance
- **Smart User Recognition**: Detects when talking to Baggins or Snazzy Daddy and avoids mentioning them to themselves
- **LLM-Powered Responses**: Uses Google Gemini 2.5 Flash to generate contextual responses
- **Conversation Memory**: Maintains short-term memory per channel (last 10 messages)
- **Emoji Reactions**: Automatically reacts to messages with relevant emojis
- **Dynamic Status**: Changes bot status every 30 minutes with random messages
- **Colorful Logging**: Uses colorama for timestamped, color-coded console logs with AI decision tracking

## Project Architecture

### Main Components
- **bot.py**: Core bot logic including Discord event handlers and message processing
- **config.py**: Configuration settings, API keys, and bot status messages
- **llm.py**: LLM integration for AI-powered responses and decision-making
- **utils.py**: Utility functions for logging and user mention handling
- **requirements.txt**: Python dependencies (discord.py, colorama, aiohttp)

### Dependencies
- `discord.py` (v2.6+): Discord API integration
- `colorama` (v0.4.6+): Terminal color formatting
- `aiohttp` (v3.13+): Async HTTP requests to Gemini API

### Environment Variables Required
- `DISCORD_BOT_TOKEN`: Discord bot authentication token
- `LLM_API_KEY`: Google Gemini API key

### Bot Configuration
- **Reply Decision**: Conservative AI-powered system that defaults to NOT responding
- **Auto-Reply Triggers** (bypass AI check):
  - Direct Discord replies to the bot's messages
  - Messages that mention "Meat Bro" or tag the bot
- **AI Reply Rules** (very conservative - defaults to NO):
  - Only responds when message clearly asks for bot input
  - Will NOT interrupt conversations between users (even about gym/fitness)
  - Will NOT respond to casual statements or stories
  - Will NOT respond if bot recently replied (unless directly mentioned)
  - Explicitly avoids butting into ongoing conversations
- **User IDs**: Hardcoded IDs for @Baggins and @SnazzyDaddy mentions
- **Status Cycle**: Updates every 30 minutes

## How to Run

### Prerequisites
1. Set up the required API keys as environment variables:
   - `DISCORD_BOT_TOKEN`: Get from [Discord Developer Portal](https://discord.com/developers/applications)
   - `LLM_API_KEY`: Get from [Google AI Studio](https://aistudio.google.com/app/apikey)

### Running the Bot
The bot runs automatically via the "Discord Bot" workflow. It will:
1. Validate that API keys are set
2. Connect to Discord
3. Start responding to messages and cycling status

### Deployment
The bot is configured for **Reserved VM (Background Worker)** deployment:
- **Deployment Type**: VM (always-on background worker)
- **Run Command**: `python bot.py`
- This configuration is appropriate for Discord bots that need to maintain persistent connections

## User Preferences
None documented yet.

## Security Notes
- API keys are stored as environment variables, not in code
- .gitignore configured to prevent committing sensitive files
- Bot tokens should never be shared or committed to version control

## Future Improvements
- Consider making REPLY_CHANCE configurable via environment variable
- Add more sophisticated conversation history management
- Implement rate limiting for API calls
- Add command handling for bot configuration
