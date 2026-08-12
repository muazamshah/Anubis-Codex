# ANUBIS CODEX - API Configuration Documentation

This document explains all API requirements, configuration, and usage for the ANUBIS CODEX application.

---

## Table of Contents

1. [API Overview](#api-overview)
2. [Required APIs](#required-apis)
3. [Optional APIs](#optional-apis)
4. [Local Services](#local-services)
5. [Configuration Setup](#configuration-setup)
6. [Configuration Validation](#configuration-validation)
7. [Service Architecture](#service-architecture)
8. [Troubleshooting](#troubleshooting)

---

## API Overview

ANUBIS CODEX uses a combination of external APIs and local services to provide repository analysis and AI-powered chat functionality.

### Summary

| API/Service | Required? | Type | API Key Required |
|-------------|-----------|------|------------------|
| LLM API (OpenRouter/OpenAI) | **YES** | External | Yes |
| GitHub API | No | External | Optional |
| Embeddings (sentence-transformers) | No | Local | No |
| Vector Database (ChromaDB) | No | Local | No |

---

## Required APIs

### 1. LLM API (OpenRouter or OpenAI)

**Status:** REQUIRED  
**Purpose:** Generate AI responses for repository chat functionality  
**Configuration:** `.env` file  
**Environment Variables:**
- `OPENROUTER_API_KEY` (recommended) OR
- `OPENAI_API_KEY` (alternative)

#### Why It's Required

The LLM API is essential for Phase 3 (AI Chat) functionality. Without it, the application can still perform repository analysis (Phase 1 and Phase 2), but the chat feature will not work.

#### Configuration Example

```env
# Option 1: OpenRouter (recommended)
OPENROUTER_API_KEY=sk-or-v1-...
LLM_PROVIDER=openrouter
LLM_MODEL=openai/gpt-3.5-turbo

# Option 2: OpenAI
# OPENAI_API_KEY=sk-...
# LLM_PROVIDER=openai
# LLM_MODEL=gpt-3.5-turbo
```

#### Default Settings

- **Provider:** OpenRouter
- **Model:** `openai/gpt-3.5-turbo`
- **Max Tokens:** 1000
- **Temperature:** 0.7
- **Timeout:** 30 seconds

#### API Endpoints

- **OpenRouter:** `https://openrouter.ai/api/v1/chat/completions`
- **OpenAI:** `https://api.openai.com/v1/chat/completions`

#### How to Get an API Key

**OpenRouter (Recommended):**
1. Visit https://openrouter.ai/
2. Sign up for an account
3. Go to Keys section
4. Create a new API key
5. Copy the key to your `.env` file

**OpenAI:**
1. Visit https://platform.openai.com/
2. Sign up for an account
3. Go to API Keys section
4. Create a new API key
5. Copy the key to your `.env` file

#### Service That Uses It

- `backend/services/chat_service.py` - `ChatService` class

---

## Optional APIs

### 2. GitHub API

**Status:** OPTIONAL  
**Purpose:** Higher rate limits for repository metadata extraction  
**Configuration:** `.env` file  
**Environment Variable:** `GITHUB_TOKEN`

#### Why It's Optional

The application can work without a GitHub token by:
1. Using public GitHub API endpoints (rate limited to 60 requests/hour)
2. Falling back to direct file downloads from GitHub

With a token, you get:
- Higher rate limits (5000 requests/hour)
- Access to private repositories (if token has permissions)
- More reliable metadata extraction

#### Configuration Example

```env
GITHUB_TOKEN=ghp_...
```

#### How to Get a GitHub Token

1. Visit https://github.com/settings/tokens
2. Click "Generate new token"
3. Give it a name (e.g., "ANUBIS CODEX")
4. Select scopes (no special scopes needed for public repos)
5. Generate token
6. Copy the token to your `.env` file

#### Service That Uses It

- `backend/services/github_service.py` - `RepositoryAnalyzerService` class
- `backend/services/download_service.py` - `DownloadService` class

#### Behavior Without Token

- Repository analysis still works
- Uses public GitHub API endpoints
- May hit rate limits during heavy usage
- Falls back to ZIP downloads if git clone fails

---

## Local Services

### 3. Embedding Service (sentence-transformers)

**Status:** LOCAL  
**Purpose:** Generate embeddings for repository code chunks  
**Configuration:** `.env` file (model name only)  
**Environment Variable:** `EMBEDDING_MODEL_NAME`  
**API Key Required:** NO

#### Why It's Local

The embedding model runs locally using the `sentence-transformers` library. No external API calls are made.

#### Configuration

```env
EMBEDDING_MODEL_NAME=sentence-transformers/all-MiniLM-L6-v2
```

#### Default Model

- **Model:** `sentence-transformers/all-MiniLM-L6-v2`
- **Dimensions:** 384
- **Provider:** Local (sentence-transformers)

#### Fallback Behavior

If the model fails to load, the service uses a hash-based fallback embedding (deterministic but less accurate).

#### Service That Uses It

- `backend/services/embedding_service.py` - `EmbeddingService` class

---

### 4. Vector Database (ChromaDB)

**Status:** LOCAL  
**Purpose:** Store and retrieve code embeddings for RAG  
**Configuration:** `.env` file (path only)  
**Environment Variable:** `VECTOR_DB_PATH`  
**API Key Required:** NO

#### Why It's Local

ChromaDB runs as a local persistent database. No external API calls are made.

#### Configuration

```env
VECTOR_DB_PATH=cache/vector_db
```

#### Default Settings

- **Path:** `cache/vector_db`
- **Collection:** `repository_chunks`
- **Distance Metric:** Cosine

#### Service That Uses It

- `backend/services/vector_service.py` - `VectorService` class

---

## Configuration Setup

### Step 1: Create `.env` File

Copy the example file and fill in your API keys:

```bash
cp backend/.env.example backend/.env
```

### Step 2: Configure Required APIs

Edit `backend/.env` and add at least one LLM API key:

```env
# REQUIRED: Add at least one of these
OPENROUTER_API_KEY=your_key_here
# OR
OPENAI_API_KEY=your_key_here
```

### Step 3: Configure Optional APIs (Recommended)

```env
# OPTIONAL: Add for better GitHub integration
GITHUB_TOKEN=your_github_token_here
```

### Step 4: Verify Configuration

The application will validate configuration on startup and report any missing required APIs.

---

## Configuration Validation

The application provides a validation mechanism to check configuration status.

### Validation Endpoint

```bash
GET /api/config/status
```

### Response Format

```json
{
  "llm": {
    "status": "configured",
    "provider": "openrouter",
    "has_openrouter": true,
    "has_openai": false
  },
  "github": {
    "status": "optional",
    "has_token": true
  },
  "embedding": {
    "status": "local",
    "model": "sentence-transformers/all-MiniLM-L6-v2",
    "api_key_required": false
  },
  "vector_db": {
    "status": "local",
    "provider": "chromadb",
    "path": "cache/vector_db",
    "api_key_required": false
  }
}
```

### Status Values

- **configured:** API key is present and valid
- **missing:** Required API key is not configured
- **optional:** API is optional and not configured
- **local:** Service runs locally, no API key needed

---

## Service Architecture

### Configuration Flow

```
.env file
    ↓
config.py (loads and validates)
    ↓
Services (import from config.py)
    ↓
API Clients (use centralized config)
```

### Central Configuration Module

**File:** `backend/config.py`

This module provides:
- Single source of truth for all configuration
- Environment variable loading
- Configuration validation
- Helper methods for each service

### Usage in Services

```python
from config import get_settings

# Get settings instance
settings = get_settings()

# Access configuration
api_key = settings.OPENROUTER_API_KEY
github_token = settings.GITHUB_TOKEN
model_name = settings.EMBEDDING_MODEL_NAME

# Get service-specific config
llm_config = settings.get_llm_config()
github_config = settings.get_github_config()
embedding_config = settings.get_embedding_config()
```

---

## Troubleshooting

### LLM API Not Working

**Symptom:** Chat returns "I need an LLM API key to generate intelligent responses"

**Solution:**
1. Check that `OPENROUTER_API_KEY` or `OPENAI_API_KEY` is set in `.env`
2. Verify the API key is valid
3. Check API provider status
4. Ensure you have sufficient credits/quota

### GitHub Rate Limiting

**Symptom:** "API rate limit exceeded" errors

**Solution:**
1. Add `GITHUB_TOKEN` to `.env`
2. Restart the backend server
3. Token provides 5000 requests/hour vs 60 requests/hour without token

### Embedding Model Not Loading

**Symptom:** Embeddings use fallback hash-based method

**Solution:**
1. Ensure `sentence-transformers` is installed: `pip install sentence-transformers`
2. Check internet connection (model downloads on first use)
3. Verify sufficient disk space for model cache
4. Check `EMBEDDING_MODEL_NAME` in `.env`

### Vector Database Not Available

**Symptom:** "Vector database unavailable" errors

**Solution:**
1. Ensure `chromadb` is installed: `pip install chromadb`
2. Check write permissions for `VECTOR_DB_PATH`
3. Verify sufficient disk space
4. Check for database corruption (delete `cache/vector_db` to reset)

### Configuration Not Loading

**Symptom:** Environment variables not being read

**Solution:**
1. Ensure `.env` file is in the `backend/` directory
2. Verify file format (no spaces around `=`)
3. Restart the backend server after changing `.env`
4. Check that `python-dotenv` is installed

---

## Security Best Practices

1. **Never commit `.env` to version control**
   - `.env` is in `.gitignore`
   - Use `.env.example` as a template

2. **Rotate API keys regularly**
   - Especially if you suspect exposure

3. **Use minimal permissions**
   - GitHub token: No special scopes needed for public repos
   - Use read-only tokens when possible

4. **Monitor API usage**
   - Check OpenRouter/OpenAI dashboard for usage
   - Monitor GitHub API rate limits

5. **Don't expose API keys in logs**
   - The application never logs actual API keys
   - Only logs configuration status

---

## Environment Variables Reference

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `OPENROUTER_API_KEY` or `OPENAI_API_KEY` | LLM API key for chat functionality | `sk-or-v1-...` |

### Optional Variables

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `GITHUB_TOKEN` | GitHub API token for higher rate limits | None | `ghp_...` |
| `LLM_PROVIDER` | LLM provider to use | `openrouter` | `openai` |
| `LLM_MODEL` | Model name for LLM | `openai/gpt-3.5-turbo` | `anthropic/claude-3-opus` |
| `LLM_MAX_TOKENS` | Maximum tokens in LLM response | `1000` | `2000` |
| `LLM_TEMPERATURE` | LLM creativity (0.0-1.0) | `0.7` | `0.5` |
| `LLM_TIMEOUT` | LLM request timeout (seconds) | `30` | `60` |

### Local Configuration Variables

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `EMBEDDING_MODEL_NAME` | Sentence-transformers model | `sentence-transformers/all-MiniLM-L6-v2` | `sentence-transformers/all-mpnet-base-v2` |
| `VECTOR_DB_PATH` | ChromaDB storage path | `cache/vector_db` | `data/vector_db` |
| `CACHE_DIR` | Repository cache directory | `/tmp/anubis-codex-cache` | `./cache/repos` |

### Server Configuration Variables

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `BACKEND_HOST` | Backend server host | `127.0.0.1` | `0.0.0.0` |
| `BACKEND_PORT` | Backend server port | `8000` | `3000` |
| `VITE_API_BASE` | Frontend API base URL | `http://127.0.0.1:8000` | `http://localhost:8000` |

---

## API Status Summary

### APIs You MUST Provide

1. **LLM API Key** - Either `OPENROUTER_API_KEY` or `OPENAI_API_KEY`
   - Required for AI chat functionality
   - Without it, chat returns fallback message
   - Repository analysis still works

### APIs That Are Optional

2. **GitHub Token** - `GITHUB_TOKEN`
   - Optional but recommended
   - Increases rate limits from 60 to 5000 requests/hour
   - Application works without it

### Services That Require NO API Key

3. **Embeddings** - Uses local sentence-transformers
4. **Vector Database** - Uses local ChromaDB
5. **Repository Download** - Uses public GitHub endpoints or git clone

---

## Additional Notes

### OpenRouter Benefits

- Access to multiple LLM providers (OpenAI, Anthropic, Google, etc.)
- Unified API interface
- Competitive pricing
- No need for multiple API keys

### Model Selection

You can use any model supported by OpenRouter:

```env
LLM_MODEL=openai/gpt-3.5-turbo  # Fast, cost-effective
LLM_MODEL=openai/gpt-4          # More capable, higher cost
LLM_MODEL=anthropic/claude-3-opus  # High quality
LLM_MODEL=google/gemini-pro     # Good balance
```

Check https://openrouter.ai/models for available models.

### Rate Limits

- **OpenRouter:** Varies by model, typically generous
- **OpenAI:** Depends on your plan (free tier has limits)
- **GitHub (without token):** 60 requests/hour
- **GitHub (with token):** 5000 requests/hour

---

## Support

For issues or questions:
1. Check this documentation
2. Review the main README.md
3. Check application logs for error messages
4. Verify configuration with `/api/config/status` endpoint