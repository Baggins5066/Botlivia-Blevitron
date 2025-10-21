# Blevitron Discord Bot

## Project Status
✅ **Pure Memory-Driven Bot** - Bot generates responses entirely from conversation database (Oct 21, 2025)

### Recent Changes (Oct 21, 2025)
- **🔄 MAJOR TRANSFORMATION: Pure Memory-Driven Architecture** - Bot now has NO persona and synthesizes responses purely from database memories:
  - **Removed all persona/personality** - No predefined character, behavior rules, or user-specific traits
  - **Retrieves 40 relevant messages** (up from 5) for comprehensive context
  - **All users treated equally** - No prioritization of specific users (removed Olivia preference)
  - **Memories framed as conversation history** - LLM generates responses based solely on patterns in past messages
  - **Author attribution included** - Each memory shows who said it: `[username]: message`
  - **Broader similarity threshold (0.25)** - Captures more contextually relevant memories
  - **Neutral decision logic** - Bot decides to reply based on generic engagement heuristics
  - System instruction: "Generate responses based solely on the conversation history provided. You have no predefined personality."
  
- **ChromaDB Local Storage** - File-based vector database:
  - All message embeddings stored locally in `chroma_data/` directory
  - 636 unique messages with 768-dimensional vectors and author metadata
  - No external database dependencies - fully self-contained project
  - Easy to back up, deploy, and version control
  
- **RAG Memory System** - Vector database with semantic search:
  - ChromaDB for local vector similarity search with cosine distance
  - Google text-embedding-004 for generating 768-dimensional vectors
  - Semantic search retrieves relevant past messages before generating responses
  - Bot has "memory" of 636 unique Discord conversations
  - Easy ingestion pipeline for adding more message history
  
- **Previous improvements**:
  - Fixed mention system using regex word boundaries
  - Added DM handling to prevent crashes
  - Migrated from PostgreSQL to ChromaDB successfully
  
- Configured for VM deployment (always-on background worker)

### Main Components
- **bot.py**: Core bot logic including Discord event handlers and message processing
- **config.py**: Configuration settings and API keys (no persona - bot is pure memory-driven)
- **llm.py**: LLM integration for AI-powered responses with neutral system instructions and comprehensive memory retrieval (40 messages)
- **utils.py**: Utility functions for logging and smart user mention handling with regex
- **chromadb_storage.py**: Local vector database storage using ChromaDB with cosine similarity
- **memory_search.py**: Semantic search using vector embeddings, retrieves 40 messages with author attribution, all users treated equally
- **message_parser.py**: Parser for Discord export text files to extract message content and author information
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
4. Retrieve 40 relevant memories from past conversations when responding (with author attribution)
5. Generate responses purely from conversation patterns in the database - NO predefined personality

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
- **Local Storage**: All embeddings stored in `chroma_data/` directory with author metadata
- **Portable**: Entire database is part of the project - easy to backup and version control
- **Deduplication**: Automatic hash-based deduplication prevents duplicate messages
- **Author Tracking**: Each message includes author information for style learning
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
