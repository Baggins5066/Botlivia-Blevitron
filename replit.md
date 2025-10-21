# Blevitron Discord Bot

## Overview
This is a blank Discord bot named "Blevitron" - a simple starter template for building Discord bots. The bot connects to Discord, logs messages, and responds when mentioned.

## Project Status
✅ **Setup Complete** - Basic Discord bot ready to extend with custom features

## Recent Changes
- **2025-10-21**: Converted from Meat Bro to Blevitron
  - Removed all LLM/AI functionality
  - Simplified to basic Discord bot template
  - Removed persona and user-specific logic
  - Renamed to Blevitron throughout codebase
  - Cleaned up config and utilities

## Features
- **Basic Message Logging**: Logs all incoming messages with timestamps
- **Mention Response**: Responds with a greeting when the bot is mentioned
- **Dynamic Status**: Changes bot status every hour from a list of statuses
- **Colorful Logging**: Uses colorama for timestamped, color-coded console logs

## Project Architecture

### Main Components
- **bot.py**: Core bot logic including Discord event handlers and message processing
- **config.py**: Configuration settings and bot status messages
- **llm.py**: Placeholder file for future LLM integration
- **utils.py**: Utility functions for logging
- **requirements.txt**: Python dependencies (discord.py, colorama)

### Dependencies
- `discord.py` (v2.6+): Discord API integration
- `colorama` (v0.4.6+): Terminal color formatting
- `aiohttp` (v3.13+): Async HTTP requests (available for future use)

### Environment Variables Required
- `DISCORD_BOT_TOKEN`: Discord bot authentication token

### Bot Configuration
- **Bot Name**: Blevitron
- **Reply Behavior**: Only responds when mentioned
- **Status Cycle**: Updates every hour
- **Statuses**: Simple, friendly status messages

## How to Run

### Prerequisites
1. Set up the required API key as an environment variable:
   - `DISCORD_BOT_TOKEN`: Get from [Discord Developer Portal](https://discord.com/developers/applications)

### Running the Bot
The bot runs automatically via the "Discord Bot" workflow. It will:
1. Validate that the Discord bot token is set
2. Connect to Discord
3. Start responding to mentions and cycling status

### Deployment
The bot is configured for **Reserved VM (Background Worker)** deployment:
- **Deployment Type**: VM (always-on background worker)
- **Run Command**: `python bot.py`
- This configuration is appropriate for Discord bots that need to maintain persistent connections

## User Preferences
None documented yet.

## Security Notes
- Bot token is stored as an environment variable, not in code
- .gitignore configured to prevent committing sensitive files
- Bot tokens should never be shared or committed to version control

## Future Improvements
- Add command handling (e.g., using discord.py commands extension)
- Add more sophisticated message responses
- Implement custom commands and features
- Add database integration for persistent storage
- Consider adding LLM integration for AI-powered responses
