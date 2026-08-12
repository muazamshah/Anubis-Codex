# ANUBIS CODEX - Architecture & How It Works

## System Architecture

ANUBIS CODEX is a **full-stack AI-powered GitHub repository analysis and chat application**. It uses a modern web stack with AI capabilities.

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         USER                                 │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│              FRONTEND (React + Vite)                         │
│  - User Interface                                            │
│  - Repository URL Input                                      │
│  - File Explorer                                             │
│  - Chat Interface                                            │
│  - Search Functionality                                      │
└───────────────────────┬─────────────────────────────────────┘
                        │ HTTP Requests (via Vite Proxy)
                        ▼
┌─────────────────────────────────────────────────────────────┐
│              BACKEND (FastAPI - Python)                      │
│  - API Endpoints                                             │
│  - Repository Download & Analysis                            │
│  - Code Parsing & Chunking                                   │
│  - Embedding Generation                                      │
│  - Vector Database Management                                │
│  - AI Chat Engine                                            │
└───────────────────────┬─────────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
        ▼               ▼               ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│   OpenRouter │ │   GitHub     │ │  ChromaDB    │
│   API (LLM)  │ │   API        │ │  (Local)     │
│              │ │              │ │              │
│ - AI Chat    │ │ - Download   │ │ - Store      │
│ - Responses  │ │ - Metadata   │ │   vectors    │
│              │ │ - Rate Limit │ │ - Search     │
└──────────────┘ └──────────────┘ └──────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│              LOCAL SERVICES                                  │
│  - sentence-transformers (Embeddings)                        │
│  - ChromaDB (Vector Database)                                │
│  - File System Cache                                         │
└─────────────────────────────────────────────────────────────┘
```

---

## Main Components

### 1. Frontend (React + Vite)

**Location:** `frontend/`

**Purpose:** User interface for interacting with the application

**Key Components:**
- **LandingScreen** - Initial page where users enter GitHub repository URL
- **RepositoryHeader** - Displays repository information
- **FileExplorer** - Shows repository file structure
- **ChatInterface** - AI chat for asking questions about the repository
- **FilePreview** - View individual file contents
- **ReadmeViewer** - Display README files
- **RepositoryInfo** - Repository metadata and statistics
- **SearchResults** - Search functionality results

**Technology Stack:**
- React 18 (UI framework)
- Vite 6 (Build tool & dev server)
- Custom CSS Design System (plain CSS, no framework)
- Lucide React (Icons)
- React Markdown (Markdown rendering)
- React Syntax Highlighter (Code highlighting)

---

### 2. Backend (FastAPI - Python)

**Location:** `backend/`

**Purpose:** Server-side logic, API endpoints, and AI integration

**Key Services:**

#### a) Repository Analysis Service
- **File:** `services/github_service.py`
- **Purpose:** Parse GitHub URLs and extract repository metadata
- **Features:**
  - URL validation
  - Repository metadata extraction (description, topics, languages)
  - README fetching
  - Commit history retrieval

#### b) Download Service
- **File:** `services/download_service.py`
- **Purpose:** Download GitHub repositories
- **Methods:**
  - Git clone (with authentication if token available)
  - ZIP download (fallback method)
  - Caching to avoid re-downloading

#### c) Scanner Service
- **File:** `services/scanner_service.py`
- **Purpose:** Scan repository files and extract content
- **Features:**
  - File type detection
  - Content extraction
  - Language identification
  - File tree generation

#### d) Parser Service
- **File:** `services/parser_service.py`
- **Purpose:** Parse code files (AST parsing)
- **Features:**
  - Extract classes, functions, methods
  - Identify code structures
  - Support multiple languages

#### e) Chunk Service
- **File:** `services/chunk_service.py`
- **Purpose:** Split code into manageable chunks
- **Features:**
  - Intelligent chunking (by functions, classes)
  - Preserve context
  - Optimize for embedding

#### f) Embedding Service
- **File:** `services/embedding_service.py`
- **Purpose:** Generate embeddings for code chunks
- **Technology:** sentence-transformers (local)
- **Model:** all-MiniLM-L6-v2 (384 dimensions)
- **Features:**
  - Batch embedding generation
  - Caching
  - Fallback to hash-based embeddings

#### g) Vector Service
- **File:** `services/vector_service.py`
- **Purpose:** Store and retrieve embeddings
- **Technology:** ChromaDB (local)
- **Features:**
  - Persistent storage
  - Similarity search
  - Filtering by repository/language

#### h) Chat Service
- **File:** `services/chat_service.py`
- **Purpose:** AI-powered chat with repository context
- **Technology:** OpenRouter API
- **Features:**
  - Context retrieval from vector DB
  - Prompt engineering
  - Streaming responses
  - Session management

#### i) Context Service
- **File:** `services/context_service.py`
- **Purpose:** Build context for chat from repository
- **Features:**
  - Retrieve relevant chunks
  - Rank by relevance
  - Build context window

#### j) Retrieval Service
- **File:** `services/retrieval_service.py`
- **Purpose:** Retrieve relevant code chunks
- **Features:**
  - Vector similarity search
  - Reranking
  - Filtering

---

### 3. API Routes

**Location:** `backend/api/routes/`

**Purpose:** HTTP endpoints for frontend communication

#### Repository Routes (`repository.py`)
- `POST /api/analyze` - Analyze a GitHub repository
- `GET /api/repository/status` - Get repository analysis status
- `POST /api/repository/chat` - Chat with specific repository
- `GET /api/config/status` - Get configuration status

#### Phase 2 Routes (`phase2.py`)
- `POST /api/embeddings/create` - Create embeddings for files
- `POST /api/retrieve` - Retrieve relevant chunks
- `POST /api/search` - Search across repositories
- `GET /api/status` - Get Phase 2 system status
- `DELETE /api/cache/clear` - Clear cache
- `DELETE /api/vector/clear` - Clear vector database

#### Phase 3 Routes (`phase3.py`)
- `POST /api/chat` - Send chat message
- `POST /api/chat/stream` - Stream chat response
- `POST /api/session/create` - Create chat session
- `POST /api/session/delete` - Delete session
- `GET /api/history` - Get chat history
- `DELETE /api/history/clear` - Clear chat history
- `GET /api/sessions` - List all sessions
- `GET /api/status` - Get Phase 3 system status

---

### 4. Configuration System

**Location:** `backend/config.py`

**Purpose:** Centralized configuration management

**Features:**
- Single source of truth for all configuration
- Environment variable loading
- Configuration validation
- Helper methods for each service

**Configuration:**
- LLM API keys (OpenRouter/OpenAI)
- GitHub token
- Embedding model settings
- Vector database path
- Cache directory
- API endpoints

---

## How It Works - Complete Flow

### 1. Repository Analysis Flow

```
User enters GitHub URL
    ↓
Frontend sends POST /api/analyze
    ↓
Backend: Parse URL (github_service.py)
    ↓
Backend: Download repository (download_service.py)
    ↓
Backend: Scan files (scanner_service.py)
    ↓
Backend: Extract metadata (metadata_service.py)
    ↓
Backend: Parse code (parser_service.py)
    ↓
Backend: Chunk files (chunk_service.py)
    ↓
Backend: Generate embeddings (embedding_service.py)
    ↓
Backend: Store in vector DB (vector_service.py)
    ↓
Return results to frontend
    ↓
Display repository analysis
```

### 2. Chat Flow

```
User asks question in chat
    ↓
Frontend sends POST /api/repository/chat
    ↓
Backend: Create/retrieve session (session_service.py)
    ↓
Backend: Validate and optimize query (query_service.py)
    ↓
Backend: Build context (context_service.py)
    │  - Generate query embedding
    │  - Search vector DB for relevant chunks
    │  - Retrieve top-k similar code snippets
    ↓
Backend: Build prompt (prompt_service.py)
    │  - System prompt
    │  - Repository context
    │  - Chat history
    │  - User question
    ↓
Backend: Call LLM (chat_service.py)
    │  - Send to OpenRouter API
    │  - Get AI response
    ↓
Backend: Save to memory (memory_service.py)
    ↓
Return response to frontend
    ↓
Display answer with sources
```

### 3. Search Flow

```
User enters search query
    ↓
Frontend sends POST /api/search
    ↓
Backend: Generate query embedding
    ↓
Backend: Search vector DB (vector_service.py)
    ↓
Backend: Rerank results (retrieval_service.py)
    ↓
Backend: Filter results
    ↓
Return search results to frontend
    ↓
Display results with file references
```

---

## Technologies Used

### Frontend
- **React 18.3** - UI framework
- **Vite 6.0** - Build tool and dev server
- **Custom CSS Design System** - Plain CSS (no Tailwind/framework)
- **Lucide React 0.468** - Icon library
- **React Markdown 9.0** - Markdown rendering
- **React Syntax Highlighter 15.5** - Code syntax highlighting

### Backend
- **FastAPI** - Modern Python web framework
- **Uvicorn** - ASGI server
- **Pydantic** - Data validation
- **Python-dotenv** - Environment variable management

### AI/ML
- **OpenRouter API** - LLM provider (OpenAI, Anthropic, etc.)
- **sentence-transformers** - Local embedding model
- **all-MiniLM-L6-v2** - Embedding model (384 dimensions)

### Data Storage
- **ChromaDB** - Vector database for embeddings
- **File System** - Repository caching
- **JSON** - Session and chat history storage

### External APIs
- **GitHub API** - Repository metadata and downloading
- **OpenRouter API** - AI chat completions

---

## Data Flow

### Repository Analysis Data Flow

```
GitHub Repository
    ↓
Download (git clone / ZIP)
    ↓
File System Cache
    ↓
Scan & Extract Content
    ↓
Parse Code (AST)
    ↓
Chunk into Pieces
    ↓
Generate Embeddings (384-dim vectors)
    ↓
Store in ChromaDB
    ↓
Ready for Search & Chat
```

### Chat Data Flow

```
User Question
    ↓
Query Embedding (384-dim vector)
    ↓
Vector Similarity Search
    ↓
Retrieve Top-K Code Chunks
    ↓
Build Context
    ↓
Construct Prompt
    ↓
Send to OpenRouter API
    ↓
Receive AI Response
    ↓
Display to User
```

---

## Key Features

### 1. Repository Analysis
- Download any public GitHub repository
- Extract metadata, README, languages, topics
- Parse code structure (classes, functions)
- Generate semantic embeddings
- Store in vector database

### 2. Semantic Search
- Search repository code using natural language
- Find relevant code snippets
- Filter by language, file, repository
- Rerank results by relevance

### 3. AI Chat
- Chat with repository using natural language
- Context-aware responses
- Source citations
- Conversation history
- Session management

### 4. File Exploration
- Browse repository structure
- View file contents
- Syntax highlighting
- File type icons

---

## Why This Architecture?

### Centralized Configuration
- Single source of truth for API keys
- Easy to manage and update
- No hardcoded secrets
- Clear validation

### Local Embeddings
- No external API dependency
- Privacy (code stays local)
- Fast inference
- Cost-effective

### Vector Database
- Fast similarity search
- Persistent storage
- Scalable to large codebases
- Supports filtering

### OpenRouter Integration
- Access to multiple LLM providers
- Unified API interface
- Competitive pricing
- Easy to switch models

---

## Performance Considerations

### Embedding Generation
- Batch processing for efficiency
- Caching to avoid regeneration
- Fallback for model failures

### Vector Search
- ChromaDB optimized for speed
- Cosine similarity metric
- Top-k retrieval
- Filtering to reduce search space

### Caching
- Repository caching (avoid re-download)
- Embedding caching (avoid regeneration)
- Session persistence

### API Optimization
- Connection pooling
- Request timeouts
- Error handling
- Rate limit management

---

## Security Considerations

### API Keys
- Stored in .env (not in git)
- Loaded at runtime
- Never exposed to frontend
- Centralized management

### CORS
- Configured to allow frontend origin
- Credentials supported
- Methods and headers restricted

### Input Validation
- URL validation
- Query sanitization
- File path security
- Error handling

---

## Scalability

### Current Architecture
- Single server deployment
- Local vector database
- File-based caching
- Suitable for personal use

### Scaling Options
- Deploy backend to cloud (Render, Railway)
- Use managed vector DB (Pinecone, Weaviate)
- Add Redis for caching
- Load balancer for multiple instances
- CDN for frontend

---

## Summary

ANUBIS CODEX is a modern, full-stack application that combines:
- **React** for the user interface
- **FastAPI** for the backend API
- **AI/ML** for intelligent code analysis and chat
- **Vector database** for semantic search
- **Local embeddings** for privacy and speed
- **OpenRouter** for flexible LLM access

The architecture is designed to be:
- **Maintainable** - Centralized configuration, clear separation of concerns
- **Scalable** - Can be deployed to cloud services
- **Secure** - No hardcoded secrets, proper validation
- **User-friendly** - Modern UI, fast responses, helpful error messages

The application can analyze any public GitHub repository and allow users to chat with it using AI, making it a powerful tool for understanding codebases quickly.