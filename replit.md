# Blevitron Discord Bot

## Project Status
✅ **Production Ready with RAG Memory** - Bot tested with semantic memory system (Oct 21, 2025)

### Recent Changes (Oct 21, 2025)
- **Migrated to ChromaDB for Local Storage** - Moved from PostgreSQL to file-based ChromaDB:
  - All message embeddings now stored locally in `chroma_data/` directory (3.6MB)
  - No external database dependencies - fully self-contained project
  - 482 unique messages with 768-dimensional vectors
  - Migrated from PostgreSQL successfully with hash-based deduplication
  - Easy to back up, deploy, and version control
- **RAG Memory System** - Vector database with semantic search:
  - ChromaDB for local vector similarity search with cosine distance
  - Google text-embedding-004 for generating 768-dimensional vectors
  - Semantic search retrieves relevant past messages before generating responses
  - Bot has "memory" of 480+ unique Discord conversations
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
- **chromadb_storage.py**: Local vector database storage using ChromaDB with cosine similarity
- **memory_search.py**: Semantic search using vector embeddings to find relevant past messages
- **message_parser.py**: Parser for Discord export text files to extract clean message content
- **embedding_pipeline.py**: Pipeline to generate embeddings and store them in ChromaDB
- **migrate_postgres_to_chromadb.py**: One-time migration script from PostgreSQL to ChromaDB
- **requirements.txt**: Python dependencies (discord.py, colorama, aiohttp, chromadb)

### Dependencies
- `discord.py` (v2.6+): Discord API integration
- `colorama` (v0.4.6+): Terminal color formatting
- `aiohttp` (v3.13+): Async HTTP requests to Gemini API
- `chromadb` (v1.2+): Local vector database for semantic similarity search

### Environment Variables Required
- `DISCORD_BOT_TOKEN`: Discord bot authentication token
- `LLM_API_KEY`: Google Gemini API key for embeddings and responses

### Prerequisites
1. Set up the required API keys as environment variables:
   - `DISCORD_BOT_TOKEN`: Get from [Discord Developer Portal](https://discord.com/developers/applications)
   - `LLM_API_KEY`: Get from [Google AI Studio](https://aistudio.google.com/app/apikey)

### Running the Bot
The bot runs automatically via the "Discord Bot" workflow. It will:
1. Validate that API keys are set
2. Connect to Discord
3. Load local ChromaDB vector database from `chroma_data/` directory
4. Retrieve relevant memories from past conversations when responding
5. Start responding to messages with context-aware AI

### Adding More Training Data
To add more Discord message history to the bot's memory:
1. Place Discord export `.txt` files in the `attached_assets/` folder
2. Run: `python embedding_pipeline.py`
3. The script will automatically:
   - Parse messages from all .txt files
   - Generate embeddings using Google's API
   - Store them in ChromaDB (stored in `chroma_data/` directory)
   - Skip any duplicate messages automatically
4. Bot will immediately have access to the new memories

### Data Storage
- **Local Storage**: All embeddings stored in `chroma_data/` directory (currently 3.6MB)
- **Portable**: Entire database is part of the project - easy to backup and version control
- **Deduplication**: Automatic hash-based deduplication prevents duplicate messages
- **By default, `chroma_data/` is committed to git** - to exclude it, uncomment the line in `.gitignore`

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
