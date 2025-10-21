# Blevitron Discord Bot

## Project Status
✅ **Production Ready with RAG Memory** - Bot tested with semantic memory system (Oct 21, 2025)

### Recent Changes (Oct 21, 2025)
- **RAG Memory System Implemented** - Added vector database with 1,000+ message embeddings:
  - PostgreSQL with pgvector extension for semantic search
  - Google text-embedding-004 for generating 768-dimensional vectors
  - Semantic search retrieves relevant past messages before generating responses
  - Bot now has "memory" of 1,008+ past Discord conversations
  - Easy ingestion pipeline for adding more message history
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
- **llm.py**: LLM integration for AI-powered responses and decision-making with memory retrieval
- **utils.py**: Utility functions for logging and smart user mention handling with regex
- **memory_search.py**: Semantic search using vector embeddings to find relevant past messages
- **message_parser.py**: Parser for Discord export text files to extract clean message content
- **embedding_pipeline.py**: Pipeline to generate embeddings and store them in PostgreSQL
- **requirements.txt**: Python dependencies (discord.py, colorama, aiohttp, psycopg2-binary, pgvector)

### Dependencies
- `discord.py` (v2.6+): Discord API integration
- `colorama` (v0.4.6+): Terminal color formatting
- `aiohttp` (v3.13+): Async HTTP requests to Gemini API
- `psycopg2-binary` (v2.9+): PostgreSQL database adapter
- `pgvector` (v0.4+): Vector similarity search extension for PostgreSQL
- `numpy` (v2.3+): Array operations for vector embeddings

### Environment Variables Required
- `DISCORD_BOT_TOKEN`: Discord bot authentication token
- `LLM_API_KEY`: Google Gemini API key
- `DATABASE_URL`: PostgreSQL connection string (automatically set by Replit)

### Prerequisites
1. Set up the required API keys as environment variables:
   - `DISCORD_BOT_TOKEN`: Get from [Discord Developer Portal](https://discord.com/developers/applications)
   - `LLM_API_KEY`: Get from [Google AI Studio](https://aistudio.google.com/app/apikey)

### Running the Bot
The bot runs automatically via the "Discord Bot" workflow. It will:
1. Validate that API keys are set
2. Connect to Discord and PostgreSQL database
3. Retrieve relevant memories from past conversations when responding
4. Start responding to messages with context-aware AI

### Adding More Training Data
To add more Discord message history to the bot's memory:
1. Place Discord export `.txt` files in the `attached_assets/` folder
2. Run: `python embedding_pipeline.py`
3. The script will automatically parse, embed, and store all messages
4. Bot will immediately have access to the new memories

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
