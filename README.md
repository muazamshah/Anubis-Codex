# ANUBIS CODEX

AI-powered GitHub Repository Intelligence Assistant with RAG (Retrieval-Augmented Generation).

## Features

- **Repository Analysis**: Paste any GitHub repository URL and get comprehensive analysis
- **RAG-Powered Chat**: Ask questions about the repository and get accurate, context-aware answers
- **File Structure Viewer**: Browse repository files with search functionality
- **Syntax Highlighting**: View code with proper syntax highlighting
- **Session History**: All chat sessions are saved locally in your browser
- **Dark/Light Mode**: Toggle between themes
- **Export Chat**: Download chat responses as Markdown files
- **Streaming Responses**: Real-time AI response streaming
- **Repository Caching**: Downloaded repositories are cached for faster subsequent access

## Architecture

### Backend (FastAPI)
- **GitHub Service**: Fetches repository metadata and README
- **Download Service**: Downloads and caches repositories
- **Parser Service**: Extracts code structure and content
- **Chunk Service**: Splits documents into manageable chunks
- **Embedding Service**: Generates embeddings using Sentence Transformers
- **Vector Service**: Stores and searches embeddings using ChromaDB
- **Chat Service**: Handles AI conversations with OpenRouter/OpenAI

### Frontend (React + Vite + Custom CSS)
- Modern, responsive UI with a custom plain-CSS design system (no framework)
- Real-time streaming chat interface
- File preview with syntax highlighting
- Session management and history
- Repository structure browser

## Prerequisites

- Python 3.9+
- Node.js 18+
- Git
- OpenRouter API key or OpenAI API key
- GitHub token (optional, for higher rate limits)

## Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd anubis-codex
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create environment file
cp .env.example .env
```

Edit `.env` and add your API keys:

```env
GITHUB_TOKEN=your_github_token_here
OPENROUTER_API_KEY=your_openrouter_api_key_here
# OR
OPENAI_API_KEY=your_openai_api_key_here
```

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install
```

### 4. Configure Vite (Optional)

If your backend runs on a different port, update `vite.config.js`:

```javascript
export default {
  server: {
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      }
    }
  }
}
```

## Running the Application

### Start Backend

```bash
cd backend
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

The API will be available at `http://127.0.0.1:8000`

### Start Frontend

```bash
cd frontend
npm run dev
```

The application will open at `http://localhost:5173`

## Usage

1. **Analyze a Repository**:
   - Paste a GitHub repository URL (e.g., `https://github.com/user/project`)
   - Click "Analyze repository"
   - Wait for the analysis to complete

2. **Ask Questions**:
   - Type your question in the chat input
   - Click "Ask ANUBIS" or press Enter
   - View the AI-powered response based on repository context

3. **Browse Files**:
   - Use the repository structure panel on the right
   - Search for specific files
   - Click on any file to preview its content

4. **Manage Sessions**:
   - View chat history in the sidebar
   - Load previous sessions
   - Export chat as Markdown
   - Copy responses to clipboard

## API Endpoints

### POST /api/analyze
Analyzes a GitHub repository and returns metadata, structure, and file contents.

**Request:**
```json
{
  "url": "https://github.com/user/repo"
}
```

**Response:**
```json
{
  "metadata": {
    "name": "user/repo",
    "description": "...",
    "languages": ["Python", "JavaScript"],
    "topics": ["machine-learning"],
    "readme": "...",
    "commit_history": [...]
  },
  "structure": {
    "files": [...],
    "count": 42,
    "languages": ["python", "javascript"]
  },
  "files": [...]
}
```

### POST /api/chat
Asks a question about the repository and returns an AI-generated answer.

**Request:**
```json
{
  "url": "https://github.com/user/repo",
  "question": "Where is authentication implemented?"
}
```

**Response:**
```json
{
  "answer": "Authentication is implemented in...",
  "metadata": {...},
  "hits": [...]
}
```

### POST /api/chat/stream
Streaming version of the chat endpoint for real-time responses.

## Ignored Directories and Files

The system automatically ignores:
- **Directories**: `node_modules`, `.git`, `build`, `dist`, `venv`, `__pycache__`, `.venv`
- **Files**: `package-lock.json`, `yarn.lock`

## Supported Languages

- Python (.py)
- JavaScript (.js, .jsx)
- TypeScript (.ts, .tsx)
- C++ (.cpp, .cc, .cxx)
- Java (.java)
- Markdown (.md)

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GITHUB_TOKEN` | GitHub API token for higher rate limits | No |
| `OPENROUTER_API_KEY` | OpenRouter API key for AI chat | Yes* |
| `OPENAI_API_KEY` | OpenAI API key (alternative to OpenRouter) | Yes* |

*At least one AI API key is required for chat functionality.

## Troubleshooting

### Backend Issues

1. **Import Errors**: Ensure all dependencies are installed: `pip install -r requirements.txt`
2. **Git Not Found**: Install Git and ensure it's in your PATH
3. **Rate Limiting**: Use a GitHub token to avoid API rate limits
4. **ChromaDB Errors**: ChromaDB may have compatibility issues. Try downgrading: `pip install chromadb==0.4.24`

### Frontend Issues

1. **CORS Errors**: Ensure the backend is running and CORS is configured correctly
2. **Module Not Found**: Run `npm install` to install all dependencies
3. **Build Errors**: Clear cache and reinstall: `rm -rf node_modules && npm install`

## Development

### Project Structure

```
anubis-codex/
├── backend/
│   ├── api/
│   │   └── routes/
│   │       └── repository.py
│   ├── services/
│   │   ├── chat_service.py
│   │   ├── chunk_service.py
│   │   ├── download_service.py
│   │   ├── embedding_service.py
│   │   ├── github_service.py
│   │   ├── parser_service.py
│   │   └── vector_service.py
│   ├── main.py
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── styles.css
│   ├── package.json
│   ├── vite.config.js
│   └── postcss.config.js
└── README.md
```

### Adding New Features

1. **Backend**: Add new services in `backend/services/`
2. **API Routes**: Add new endpoints in `backend/api/routes/`
3. **Frontend**: Update components in `frontend/src/`

## Future Improvements

- [ ] Multi-repository support
- [ ] Commit analysis and history visualization
- [ ] Pull request analysis
- [ ] Automatic documentation generation
- [ ] Security vulnerability detection
- [ ] Code quality metrics
- [ ] Interactive code exploration
- [ ] Dependency graph visualization

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.