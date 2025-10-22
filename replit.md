# Blevitron Discord Bot

## Project Status
✅ **Memory-Driven Bot with User Profiles** - Bot generates personalized responses using conversation database + user profiles (Oct 21, 2025)

### Recent Changes (Oct 22, 2025)
- **🎭 NEW: Memory-Driven Personality System** - Bot learns speaking style from conversation history:
  - **Database memories = Speaking style source** - The 636+ messages in ChromaDB teach the bot how to talk, its tone, and personality patterns
  - **User profiles = Factual context only** - Each profile provides relationship background, history, and contextual information about that person
  - **Natural personality emergence** - Bot mimics its past speaking patterns instead of following scripted personality instructions
  - **Context-aware responses** - Profiles provide facts like "This is Aiden, your ex-boyfriend" while memories show how you actually spoke
  - Converted all user profiles from behavioral instructions to factual relationship context

- **🔧 User Recognition System** - Bot now properly recognizes people:
  - **Live message storage** - All new conversations are automatically saved to ChromaDB with proper usernames
  - **User mention cleaning** - Discord user IDs like `<@123456>` are replaced with `[user]` placeholder
  - **Unique message IDs** - Uses Discord message IDs to prevent data loss from duplicate messages
  - **Clean prompts** - Both short-term history and current messages are sanitized before sending to LLM
  - **Author attribution** - Every stored message includes the proper display name of who said it
  - No more user ID confusion - bot responds using actual usernames instead of numeric IDs

### Recent Changes (Oct 21, 2025)
- **✨ User Profile System** - Local JSON file storage for relationship context:
  - **Factual relationship context** - Store background information about your relationship with each Discord user
  - **Profile commands** - Easy-to-use Discord commands for managing profiles (`!setdesc`, `!profile`, etc.)
  - **Context-aware responses** - Bot uses profile facts alongside conversation memories for informed responses
  - **Local JSON storage** - Profiles stored in `user_data/profiles.json` (portable, editable, version-controllable)
  - **Profile context injection** - Automatically loaded when responding to each user
  - **No database required** - Works outside Replit, completely self-contained
  
- **🔄 Memory-Driven Speaking Style** - Bot learns how to talk from database memories:
  - **No predefined persona/personality** - No hardcoded character traits or scripted instructions
  - **Retrieves 40 relevant messages** to learn speaking patterns and style
  - **Memories teach personality** - LLM studies past messages to understand tone, word choice, and conversational style
  - **Author attribution included** - Each memory shows who said it: `[username]: message`
  - **Broader similarity threshold (0.25)** - Captures more contextually relevant memories
  - **Neutral decision logic** - Bot decides to reply based on engagement heuristics
  - System instruction emphasizes learning from conversation history, not profile instructions
  
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
- **bot.py**: Core bot logic including Discord event handlers, message processing, live message storage, and profile management commands
- **message_storage.py**: Async message storage handler that cleans and stores live Discord messages in ChromaDB
- **config.py**: Configuration settings and API keys
- **llm.py**: LLM integration for AI-powered responses - learns speaking style from memories, uses profiles for factual context (retrieves 40 messages)
- **user_profiles_local.py**: Local JSON file operations for user profile management (CRUD operations)
- **utils.py**: Utility functions for logging and smart user mention handling with regex
- **chromadb_storage.py**: Local vector database storage using ChromaDB with cosine similarity
- **memory_search.py**: Semantic search using vector embeddings, retrieves 40 messages with author attribution
- **message_parser.py**: Parser for Discord export text files to extract and clean message content and author information
- **embedding_pipeline.py**: Pipeline to generate embeddings and store them in ChromaDB
- **migrate_postgres_to_local.py**: One-time migration script from PostgreSQL to local JSON storage
- **requirements.txt**: Python dependencies (discord.py, colorama, aiohttp, chromadb)

### Dependencies
- `discord.py` (v2.6+): Discord API integration
- `colorama` (v0.4.6+): Terminal color formatting
- `aiohttp` (v3.13+): Async HTTP requests to Gemini API
- `chromadb` (v1.2+): Local vector database for semantic similarity search
- `numpy`: Numerical operations for embeddings

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
4. Load user profiles from local `user_data/profiles.json` file
5. When responding, retrieve:
   - 40 relevant memories from past conversations to learn speaking style and patterns
   - User profile information for factual context about relationships (if available)
6. Generate responses by mimicking past conversation style and incorporating relationship context

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
- **ChromaDB (Local)**: All conversation embeddings stored in `chroma_data/` directory with author metadata
  - Portable - entire database is part of the project
  - Automatic hash-based deduplication
  - By default, `chroma_data/` is committed to git
  
- **User Profiles (Local JSON)**: User information stored in `user_data/profiles.json`
  - **Human-readable** - Easy to edit manually in any text editor
  - **Portable** - Works outside of Replit, no database needed
  - **Version-controllable** - Can be committed to git
  - **Thread-safe** - File locking prevents concurrent write issues
  - **Simple structure** - Each user has a description field storing factual relationship context
  - **Easy backup** - Simply copy the JSON file

### Migrating from PostgreSQL to Local Storage
If you have existing user profile data in PostgreSQL and want to migrate to local JSON storage:

1. **Temporarily install PostgreSQL driver:**
   ```bash
   pip install psycopg2-binary
   ```

2. **Run the migration script:**
   ```bash
   python migrate_postgres_to_local.py
   ```

3. **Verify the migration:**
   - Check that `user_data/profiles.json` contains your data
   - Test the bot to ensure profiles load correctly

4. **Clean up (optional):**
   ```bash
   pip uninstall psycopg2-binary
   ```

**Note:** Fresh installations don't need migration - the bot will automatically create the JSON file when you add your first profile.

### Managing User Profiles
Use Discord commands to manage user relationship context:

**View a profile:**
```
!profile @username
!profile  (view your own profile)
```

**Set factual context about your relationship with a user:**
```
!setdesc @Baggins This is Aiden, your ex-boyfriend from a few years ago. You still have feelings for him.
```

**List all profiles:**
```
!profiles
```

**Get help:**
```
!help
```

The description provides factual context about your relationship with that user. Include background information, relationship history, or contextual details. The bot learns its speaking style from past conversations in the database, not from profile instructions.

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
