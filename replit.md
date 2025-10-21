# Blevitron Discord Bot

## Project Status
✅ **Production Ready** - Bot tested, debugged, and ready to publish (Oct 21, 2025)

### Recent Changes (Oct 21, 2025)
- Code analysis and bug fixes:
  - **Removed status cycling feature** - Eliminated unused status generation to simplify bot
  - **Fixed personalized responses** - Now properly passes user Discord IDs to AI for persona-based interactions
  - **Fixed mention system** - Rewrote mention replacement using regex word boundaries to prevent partial word matches (e.g., "liv" no longer matches inside "living")
- Previous fixes:
  - Added DM handling to prevent crashes when receiving direct messages
  - Bot persona and personalized user interactions in config.py
- Configured for VM deployment (always-on background worker)

### Main Components
- **bot.py**: Core bot logic including Discord event handlers and message processing
- **config.py**: Configuration settings, API keys, and personalized bot personas for each user
- **llm.py**: LLM integration for AI-powered responses and decision-making
- **utils.py**: Utility functions for logging and smart user mention handling with regex
- **requirements.txt**: Python dependencies (discord.py, colorama, aiohttp)

### Dependencies
- `discord.py` (v2.6+): Discord API integration
- `colorama` (v0.4.6+): Terminal color formatting
- `aiohttp` (v3.13+): Async HTTP requests to Gemini API

### Environment Variables Required
- `DISCORD_BOT_TOKEN`: Discord bot authentication token
- `LLM_API_KEY`: Google Gemini API key

### Prerequisites
1. Set up the required API keys as environment variables:
   - `DISCORD_BOT_TOKEN`: Get from [Discord Developer Portal](https://discord.com/developers/applications)
   - `LLM_API_KEY`: Get from [Google AI Studio](https://aistudio.google.com/app/apikey)

### Running the Bot
The bot runs automatically via the "Discord Bot" workflow. It will:
1. Validate that API keys are set
2. Connect to Discord
3. Start responding to messages

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
