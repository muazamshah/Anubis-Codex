import { useCallback, useEffect, useMemo, useState } from 'react';
import { 
  Bot, ChevronRight, FileCode, FolderOpen, Moon, Search, Sun, X, 
  Database, Cpu, Activity, Layers, BarChart3, Loader2, Send, 
  MessageSquare, Trash2, User, History
} from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism';

const API_BASE = '';

const initialState = {
  status: 'idle',
  repository: null,
  metadata: null,
  files: [],
  fileCount: 0,
  languages: [],
  tree: {},
  selectedFile: null,
  error: null,
  // Phase 2 state
  phase2: {
    chunks: 0,
    embeddings: 0,
    searchResults: [],
    isIndexing: false,
    indexingProgress: null,
    vectorStats: null,
    cacheStats: null,
  },
  // Phase 3 state
  phase3: {
    sessionId: null,
    messages: [],
    isChatLoading: false,
    chatError: null,
  }
};

function App() {
  const [url, setUrl] = useState('https://github.com/openai/openai-cookbook');
  const [result, setResult] = useState(initialState);
  const [loading, setLoading] = useState(false);
  const [darkMode, setDarkMode] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedFileContent, setSelectedFileContent] = useState(null);
  const [activeTab, setActiveTab] = useState('phase1'); // 'phase1', 'phase2', 'phase3'
  const [searchText, setSearchText] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [isSearching, setIsSearching] = useState(false);
  
  // Chat state
  const [chatMessage, setChatMessage] = useState('');
  const [isChatting, setIsChatting] = useState(false);

  const summary = useMemo(() => {
    if (!result.repository) return 'Paste a repository URL to begin analysis.';
    const langs = result.languages?.length ? result.languages.join(', ') : 'Unknown';
    return `${result.repository.full_name} • ${langs}`;
  }, [result.repository, result.languages]);

  const filteredFiles = useMemo(() => {
    if (!searchQuery.trim() || !result.files) return result.files || [];
    const q = searchQuery.toLowerCase();
    return result.files.filter((file) => file.path.toLowerCase().includes(q));
  }, [result.files, searchQuery]);

  const analyzeRepository = async () => {
    if (!url.trim()) return;
    setLoading(true);
    setResult(initialState);
    setSelectedFileContent(null);
    try {
      const response = await fetch(`${API_BASE}/api/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url }),
      });
      if (!response.ok) throw new Error('Analysis failed');
      const data = await response.json();
      
      // Update phase2 stats if indexing was performed
      const indexingData = data.indexing || {};
      
      setResult((current) => ({
        ...current,
        status: data.status,
        repository: data.repository,
        metadata: data.metadata,
        files: data.files || [],
        fileCount: data.file_count || 0,
        languages: data.languages || [],
        tree: data.tree || {},
        phase2: {
          ...current.phase2,
          chunks: indexingData.chunks_created || 0,
          embeddings: indexingData.embeddings_generated || 0,
          vectorStats: indexingData.vector_db_updated ? { status: "active", count: indexingData.chunks_created } : null,
        }
      }));
      
      // Auto-switch to phase2 if indexing was successful
      if (indexingData.chunks_created > 0) {
        setActiveTab('phase2');
      }
    } catch (error) {
      setResult((current) => ({
        ...current,
        status: 'error',
        error: `Analysis failed: ${error.message}`,
      }));
    } finally {
      setLoading(false);
    }
  };

  const indexRepository = async () => {
    if (!result.files || result.files.length === 0) return;
    
    setResult((current) => ({
      ...current,
      phase2: {
        ...current.phase2,
        isIndexing: true,
        indexingProgress: 'Starting indexing...',
      }
    }));

    try {
      const repository_id = result.repository?.full_name || 'default';
      
      setResult((current) => ({
        ...current,
        phase2: {
          ...current.phase2,
          indexingProgress: 'Creating chunks and embeddings...',
        }
      }));

      const embeddingResponse = await fetch(`${API_BASE}/api/embeddings/create`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          repository_id,
          files: result.files,
        }),
      });

      if (!embeddingResponse.ok) throw new Error('Embedding creation failed');
      const embeddingData = await embeddingResponse.json();

      const statusResponse = await fetch(`${API_BASE}/api/status`);
      const statusData = await statusResponse.json();

      setResult((current) => ({
        ...current,
        phase2: {
          ...current.phase2,
          isIndexing: false,
          indexingProgress: null,
          chunks: embeddingData.chunks_created || 0,
          embeddings: embeddingData.embeddings_generated || 0,
          vectorStats: statusData.vector_database,
          cacheStats: statusData.cache,
        }
      }));

      setActiveTab('phase2');
    } catch (error) {
      setResult((current) => ({
        ...current,
        phase2: {
          ...current.phase2,
          isIndexing: false,
          indexingProgress: `Indexing failed: ${error.message}`,
        }
      }));
    }
  };

  const searchRepository = async () => {
    if (!searchText.trim()) return;
    
    setIsSearching(true);
    setSearchResults([]);

    try {
      const response = await fetch(`${API_BASE}/api/search`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: searchText,
          n_results: 10,
        }),
      });

      if (!response.ok) throw new Error('Search failed');
      const data = await response.json();
      setSearchResults(data.results || []);
    } catch (error) {
      console.error('Search failed:', error);
    } finally {
      setIsSearching(false);
    }
  };

  const sendChatMessage = async () => {
    if (!chatMessage.trim() || !result.repository) return;
    
    const repository_id = result.repository.full_name;
    const session_id = result.phase3.sessionId || `session_${Date.now()}`;
    
    // Create session if needed
    if (!result.phase3.sessionId) {
      try {
        const sessionResponse = await fetch(`${API_BASE}/api/session/create`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ repository_id }),
        });
        const sessionData = await sessionResponse.json();
        if (sessionData.status === 'completed') {
          setResult((current) => ({
            ...current,
            phase3: {
              ...current.phase3,
              sessionId: sessionData.session.session_id,
            }
          }));
        }
      } catch (error) {
        console.error('Session creation failed:', error);
      }
    }
    
    const userMessage = { role: 'user', content: chatMessage, timestamp: Date.now() };
    setResult((current) => ({
      ...current,
      phase3: {
        ...current.phase3,
        messages: [...current.phase3.messages, userMessage],
        isChatLoading: true,
        chatError: null,
      }
    }));
    
    setChatMessage('');
    setIsChatting(true);

    try {
      const currentSessionId = result.phase3.sessionId || session_id;
      
      // Use repository-specific chat endpoint for better context
      const response = await fetch(`${API_BASE}/api/repository/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: currentSessionId,
          question: chatMessage,
          repository_id: repository_id,
        }),
      });

      if (!response.ok) throw new Error('Chat failed');
      const data = await response.json();
      
      const assistantMessage = {
        role: 'assistant',
        content: data.answer,
        sources: data.sources,
        timestamp: Date.now(),
      };

      setResult((current) => ({
        ...current,
        phase3: {
          ...current.phase3,
          messages: [...current.phase3.messages, assistantMessage],
          isChatLoading: false,
          sessionId: data.session_id,
        }
      }));
    } catch (error) {
      setResult((current) => ({
        ...current,
        phase3: {
          ...current.phase3,
          isChatLoading: false,
          chatError: `Chat failed: ${error.message}`,
        }
      }));
    } finally {
      setIsChatting(false);
    }
  };

  const clearChatHistory = async () => {
    if (!result.phase3.sessionId) return;
    
    try {
      await fetch(`${API_BASE}/api/history/clear?session_id=${result.phase3.sessionId}`, {
        method: 'DELETE',
      });
      
      setResult((current) => ({
        ...current,
        phase3: {
          ...current.phase3,
          messages: [],
        }
      }));
    } catch (error) {
      console.error('Failed to clear history:', error);
    }
  };

  const openFile = (file) => {
    setSelectedFileContent(file);
  };

  const closeFile = () => {
    setSelectedFileContent(null);
  };

  const languageToExtension = (language) => {
    const map = {
      python: 'python',
      javascript: 'javascript',
      typescript: 'typescript',
      cpp: 'cpp',
      java: 'java',
      go: 'go',
      rust: 'rust',
      markdown: 'markdown',
    };
    return map[language] || 'text';
  };

  return (
    <div className={`min-h-screen ${darkMode ? 'bg-slate-950 text-slate-100' : 'bg-slate-50 text-slate-900'}`}>
      <div className="mx-auto flex max-w-7xl flex-col gap-4 p-4 lg:flex-row lg:p-6">
        {/* Sidebar */}
        <aside className={`w-full rounded-2xl border ${darkMode ? 'border-slate-800 bg-slate-900/80' : 'border-slate-200 bg-white'} p-5 lg:w-72`}>
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-xl font-semibold">ANUBIS CODEX</h2>
              <p className="mt-1 text-xs text-slate-400">Repository Intelligence</p>
            </div>
            <button
              onClick={() => setDarkMode((v) => !v)}
              className={`rounded-lg p-2 transition ${darkMode ? 'bg-slate-800 text-slate-200 hover:bg-slate-700' : 'bg-slate-100 text-slate-700 hover:bg-slate-200'}`}
            >
              {darkMode ? <Sun size={16} /> : <Moon size={16} />}
            </button>
          </div>

          <div className="mt-6 space-y-3">
            <div className={`rounded-xl border ${darkMode ? 'border-slate-800 bg-slate-950/70' : 'border-slate-200 bg-slate-50'} p-3`}>
              <p className="text-[11px] uppercase tracking-[0.2em] text-slate-500">Repository</p>
              <p className="mt-1 text-sm font-medium">{result.repository?.full_name || 'Waiting for input'}</p>
            </div>
            <div className={`rounded-xl border ${darkMode ? 'border-slate-800 bg-slate-950/70' : 'border-slate-200 bg-slate-50'} p-3`}>
              <p className="text-[11px] uppercase tracking-[0.2em] text-slate-500">Summary</p>
              <p className="mt-1 text-sm">{summary}</p>
            </div>
            <div className={`rounded-xl border ${darkMode ? 'border-slate-800 bg-slate-950/70' : 'border-slate-200 bg-slate-50'} p-3`}>
              <p className="text-[11px] uppercase tracking-[0.2em] text-slate-500">Files</p>
              <p className="mt-1 text-sm">{result.fileCount || 0} files analyzed</p>
            </div>
            {result.metadata?.topics?.length > 0 && (
              <div className={`rounded-xl border ${darkMode ? 'border-slate-800 bg-slate-950/70' : 'border-slate-200 bg-slate-50'} p-3`}>
                <p className="text-[11px] uppercase tracking-[0.2em] text-slate-500">Topics</p>
                <div className="mt-2 flex flex-wrap gap-1">
                  {result.metadata.topics.map((topic) => (
                    <span key={topic} className={`rounded-md px-2 py-0.5 text-[11px] ${darkMode ? 'bg-slate-800 text-slate-300' : 'bg-slate-200 text-slate-700'}`}>
                      {topic}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>

          {result.metadata?.dependencies?.length > 0 && (
            <div className="mt-6">
              <div className={`rounded-xl border ${darkMode ? 'border-slate-800 bg-slate-950/70' : 'border-slate-200 bg-slate-50'} p-3`}>
                <p className="text-[11px] uppercase tracking-[0.2em] text-slate-500">Dependencies</p>
                <div className="mt-2 max-h-48 space-y-1 overflow-y-auto text-xs">
                  {result.metadata.dependencies.slice(0, 20).map((dep, index) => (
                    <div key={index} className={`rounded px-2 py-1 ${darkMode ? 'bg-slate-800 text-slate-300' : 'bg-slate-200 text-slate-700'}`}>
                      {dep}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Phase 2 Stats */}
          {(result.phase2.chunks > 0 || result.phase2.vectorStats) && (
            <div className="mt-6">
              <div className={`rounded-xl border ${darkMode ? 'border-slate-800 bg-slate-950/70' : 'border-slate-200 bg-slate-50'} p-3`}>
                <p className="text-[11px] uppercase tracking-[0.2em] text-slate-500">Phase 2 Stats</p>
                <div className="mt-2 space-y-2 text-xs">
                  <div className="flex justify-between">
                    <span className="text-slate-400">Chunks:</span>
                    <span className="font-medium">{result.phase2.chunks || 0}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">Embeddings:</span>
                    <span className="font-medium">{result.phase2.embeddings || 0}</span>
                  </div>
                  {result.phase2.vectorStats && (
                    <div className="flex justify-between">
                      <span className="text-slate-400">Vector DB:</span>
                      <span className="font-medium">{result.phase2.vectorStats.count || 0} vectors</span>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* Phase 3 Stats */}
          {result.phase3.sessionId && (
            <div className="mt-6">
              <div className={`rounded-xl border ${darkMode ? 'border-slate-800 bg-slate-950/70' : 'border-slate-200 bg-slate-50'} p-3`}>
                <p className="text-[11px] uppercase tracking-[0.2em] text-slate-500">Phase 3 Chat</p>
                <div className="mt-2 space-y-2 text-xs">
                  <div className="flex justify-between">
                    <span className="text-slate-400">Messages:</span>
                    <span className="font-medium">{result.phase3.messages.length}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">Session:</span>
                    <span className="font-medium text-[10px]">{result.phase3.sessionId.slice(0, 8)}...</span>
                  </div>
                </div>
              </div>
            </div>
          )}
        </aside>

        {/* Main content */}
        <main className="flex-1 space-y-4">
          {/* Input section */}
          <section className={`rounded-2xl border ${darkMode ? 'border-slate-800 bg-slate-900/80' : 'border-slate-200 bg-white'} p-5`}>
            <div className="flex flex-col gap-3 md:flex-row">
              <input
                value={url}
                onChange={(event) => setUrl(event.target.value)}
                className={`flex-1 rounded-xl border px-4 py-3 text-sm outline-none transition ${
                  darkMode
                    ? 'border-slate-700 bg-slate-950 text-slate-100 focus:border-cyan-400'
                    : 'border-slate-300 bg-slate-50 text-slate-900 focus:border-cyan-500'
                }`}
                placeholder="Paste a GitHub repository URL"
              />
              <button
                onClick={analyzeRepository}
                disabled={loading}
                className="rounded-xl bg-cyan-600 px-4 py-3 text-sm font-medium text-white transition hover:bg-cyan-500 disabled:opacity-60"
              >
                {loading ? 'Analyzing...' : 'Analyze repository'}
              </button>
            </div>
            {result.error && (
              <div className="mt-3 rounded-xl border border-red-500 bg-red-500/10 p-3 text-sm text-red-400">
                {result.error}
              </div>
            )}
          </section>

          {/* Tab Navigation */}
          {result.status === 'completed' && (
            <section className="flex gap-2">
              <button
                onClick={() => setActiveTab('phase1')}
                className={`rounded-lg px-4 py-2 text-sm font-medium transition ${
                  activeTab === 'phase1'
                    ? 'bg-cyan-600 text-white'
                    : darkMode ? 'bg-slate-800 text-slate-300 hover:bg-slate-700' : 'bg-slate-200 text-slate-700 hover:bg-slate-300'
                }`}
              >
                <Database size={16} className="inline mr-2" />
                Phase 1: Analysis
              </button>
              <button
                onClick={() => setActiveTab('phase2')}
                className={`rounded-lg px-4 py-2 text-sm font-medium transition ${
                  activeTab === 'phase2'
                    ? 'bg-cyan-600 text-white'
                    : darkMode ? 'bg-slate-800 text-slate-300 hover:bg-slate-700' : 'bg-slate-200 text-slate-700 hover:bg-slate-300'
                }`}
              >
                <Cpu size={16} className="inline mr-2" />
                Phase 2: RAG
              </button>
              <button
                onClick={() => setActiveTab('phase3')}
                className={`rounded-lg px-4 py-2 text-sm font-medium transition ${
                  activeTab === 'phase3'
                    ? 'bg-cyan-600 text-white'
                    : darkMode ? 'bg-slate-800 text-slate-300 hover:bg-slate-700' : 'bg-slate-200 text-slate-700 hover:bg-slate-300'
                }`}
              >
                <MessageSquare size={16} className="inline mr-2" />
                Phase 3: Chat
              </button>
            </section>
          )}

          {/* Main panels */}
          {activeTab === 'phase1' ? (
            <section className="grid gap-4 lg:grid-cols-[1.2fr_0.8fr]">
              {/* Left panel - README and File Preview */}
              <div className="space-y-4">
                {/* README */}
                {result.metadata?.readme && (
                  <div className={`rounded-2xl border ${darkMode ? 'border-slate-800 bg-slate-900/80' : 'border-slate-200 bg-white'} p-5`}>
                    <h3 className="text-lg font-semibold">README</h3>
                    <div
                      className={`mt-4 max-h-96 overflow-y-auto rounded-xl border p-4 text-sm leading-relaxed ${
                        darkMode ? 'border-slate-800 bg-slate-950/70 text-slate-300' : 'border-slate-200 bg-slate-50 text-slate-800'
                      }`}
                    >
                      <ReactMarkdown
                        components={{
                          code({ node, inline, className, children, ...props }) {
                            const match = /language-(\w+)/.exec(className || '');
                            const language = match ? match[1] : 'text';
                            return !inline && match ? (
                              <SyntaxHighlighter
                                style={oneDark}
                                language={language}
                                PreTag="div"
                                className="rounded-lg"
                                {...props}
                              >
                                {String(children).replace(/\n$/, '')}
                              </SyntaxHighlighter>
                            ) : (
                              <code className={className} {...props}>
                                {children}
                              </code>
                            );
                          },
                        }}
                      >
                        {result.metadata.readme}
                      </ReactMarkdown>
                    </div>
                  </div>
                )}

                {/* File preview */}
                {selectedFileContent && (
                  <div className={`rounded-2xl border ${darkMode ? 'border-slate-800 bg-slate-900/80' : 'border-slate-200 bg-white'} p-5`}>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <FileCode size={18} />
                        <h3 className="text-lg font-semibold">File preview</h3>
                      </div>
                      <button
                        onClick={closeFile}
                        className={`rounded-lg p-2 transition ${darkMode ? 'text-slate-400 hover:text-slate-200' : 'text-slate-500 hover:text-slate-800'}`}
                      >
                        <X size={16} />
                      </button>
                    </div>
                    <p className="mt-2 text-xs text-slate-500">{selectedFileContent.path}</p>
                    <div
                      className={`mt-3 max-h-96 overflow-y-auto rounded-xl border p-3 text-xs ${
                        darkMode ? 'border-slate-800 bg-slate-950/70 text-slate-300' : 'border-slate-200 bg-slate-50 text-slate-800'
                      }`}
                    >
                      <SyntaxHighlighter
                        language={languageToExtension(selectedFileContent.language)}
                        style={oneDark}
                        PreTag="div"
                        showLineNumbers
                        wrapLines
                      >
                        {'// File content preview - Click to view full content'}
                      </SyntaxHighlighter>
                    </div>
                  </div>
                )}
              </div>

              {/* Right panel - Repository structure */}
              <div className={`rounded-2xl border ${darkMode ? 'border-slate-800 bg-slate-900/80' : 'border-slate-200 bg-white'} p-5`}>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <FolderOpen size={18} />
                    <h3 className="text-lg font-semibold">Repository structure</h3>
                  </div>
                  <span className="text-xs text-slate-500">{result.fileCount || 0} files</span>
                </div>
                <div className={`mt-3 flex items-center gap-2 rounded-lg border px-3 py-2 text-xs ${darkMode ? 'border-slate-800 bg-slate-950/70 text-slate-300' : 'border-slate-200 bg-slate-50 text-slate-700'}`}>
                  <Search size={14} />
                  <input
                    value={searchQuery}
                    onChange={(event) => setSearchQuery(event.target.value)}
                    className="w-full bg-transparent outline-none"
                    placeholder="Search files..."
                  />
                </div>
                <ul className="mt-3 max-h-[600px] space-y-1 overflow-y-auto text-xs">
                  {filteredFiles.length === 0 && (
                    <li className={`px-3 py-2 ${darkMode ? 'text-slate-500' : 'text-slate-400'}`}>
                      {result.status === 'completed' ? 'No files found.' : 'Analyze a repository to see files.'}
                    </li>
                  )}
                  {filteredFiles.map((file) => (
                    <li
                      key={file.path}
                      className={`flex cursor-pointer items-center gap-2 rounded-lg px-3 py-2 transition ${
                        darkMode ? 'hover:bg-slate-800 text-slate-300' : 'hover:bg-slate-100 text-slate-700'
                      }`}
                      onClick={() => openFile(file)}
                    >
                      <FileCode size={14} />
                      <span className="truncate flex-1">{file.path}</span>
                      <span className={`text-[10px] ${darkMode ? 'text-slate-500' : 'text-slate-400'}`}>{file.language}</span>
                      <ChevronRight size={14} className="ml-auto opacity-50" />
                    </li>
                  ))}
                </ul>
              </div>
            </section>
          ) : activeTab === 'phase2' ? (
            <section className="space-y-4">
              {/* Indexing Button */}
              {result.phase2.chunks === 0 && !result.phase2.isIndexing && (
                <div className={`rounded-2xl border ${darkMode ? 'border-slate-800 bg-slate-900/80' : 'border-slate-200 bg-white'} p-5`}>
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-lg font-semibold">RAG Engine</h3>
                      <p className="mt-1 text-sm text-slate-400">Index repository for semantic search</p>
                    </div>
                    <button
                      onClick={indexRepository}
                      className="rounded-xl bg-cyan-600 px-4 py-3 text-sm font-medium text-white transition hover:bg-cyan-500"
                    >
                      <Cpu size={16} className="inline mr-2" />
                      Index Repository
                    </button>
                  </div>
                </div>
              )}

              {/* Indexing Progress */}
              {result.phase2.isIndexing && (
                <div className={`rounded-2xl border ${darkMode ? 'border-slate-800 bg-slate-900/80' : 'border-slate-200 bg-white'} p-5`}>
                  <div className="flex items-center gap-3">
                    <Loader2 size={24} className="animate-spin text-cyan-500" />
                    <div>
                      <h3 className="text-lg font-semibold">Indexing in Progress</h3>
                      <p className="mt-1 text-sm text-slate-400">{result.phase2.indexingProgress}</p>
                    </div>
                  </div>
                </div>
              )}

              {/* Search Interface */}
              {result.phase2.chunks > 0 && (
                <div className={`rounded-2xl border ${darkMode ? 'border-slate-800 bg-slate-900/80' : 'border-slate-200 bg-white'} p-5`}>
                  <div className="flex items-center gap-2 mb-4">
                    <Search size={18} />
                    <h3 className="text-lg font-semibold">Semantic Search</h3>
                  </div>
                  <div className="flex gap-2">
                    <input
                      value={searchText}
                      onChange={(event) => setSearchText(event.target.value)}
                      onKeyDown={(e) => e.key === 'Enter' && searchRepository()}
                      className={`flex-1 rounded-xl border px-4 py-3 text-sm outline-none transition ${
                        darkMode
                          ? 'border-slate-700 bg-slate-950 text-slate-100 focus:border-cyan-400'
                          : 'border-slate-300 bg-slate-50 text-slate-900 focus:border-cyan-500'
                      }`}
                      placeholder="Search in repository..."
                    />
                    <button
                      onClick={searchRepository}
                      disabled={isSearching}
                      className="rounded-xl bg-cyan-600 px-4 py-3 text-sm font-medium text-white transition hover:bg-cyan-500 disabled:opacity-60"
                    >
                      {isSearching ? <Loader2 size={16} className="animate-spin" /> : 'Search'}
                    </button>
                  </div>
                </div>
              )}

              {/* Search Results */}
              {searchResults.length > 0 && (
                <div className={`rounded-2xl border ${darkMode ? 'border-slate-800 bg-slate-900/80' : 'border-slate-200 bg-white'} p-5`}>
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-2">
                      <BarChart3 size={18} />
                      <h3 className="text-lg font-semibold">Search Results</h3>
                    </div>
                    <span className="text-xs text-slate-500">{searchResults.length} results</span>
                  </div>
                  <div className="space-y-3">
                    {searchResults.map((result, index) => (
                      <div
                        key={index}
                        className={`rounded-lg border p-3 ${darkMode ? 'border-slate-800 bg-slate-950/70' : 'border-slate-200 bg-slate-50'}`}
                      >
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-xs font-medium text-cyan-400">{result.metadata?.file_path || 'Unknown'}</span>
                          <span className="text-xs text-slate-500">Score: {(result.score * 100).toFixed(1)}%</span>
                        </div>
                        <p className="text-xs text-slate-400 line-clamp-3">{result.content?.slice(0, 200)}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Vector DB Stats */}
              {result.phase2.vectorStats && (
                <div className={`rounded-2xl border ${darkMode ? 'border-slate-800 bg-slate-900/80' : 'border-slate-200 bg-white'} p-5`}>
                  <div className="flex items-center gap-2 mb-4">
                    <Activity size={18} />
                    <h3 className="text-lg font-semibold">Vector Database Status</h3>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div className={`rounded-lg border p-3 ${darkMode ? 'border-slate-800 bg-slate-950/70' : 'border-slate-200 bg-slate-50'}`}>
                      <p className="text-xs text-slate-400">Status</p>
                      <p className="text-sm font-medium mt-1">{result.phase2.vectorStats.status}</p>
                    </div>
                    <div className={`rounded-lg border p-3 ${darkMode ? 'border-slate-800 bg-slate-950/70' : 'border-slate-200 bg-slate-50'}`}>
                      <p className="text-xs text-slate-400">Total Vectors</p>
                      <p className="text-sm font-medium mt-1">{result.phase2.vectorStats.count || 0}</p>
                    </div>
                  </div>
                </div>
              )}
            </section>
          ) : (
            /* Phase 3: Chat Interface */
            <section className={`rounded-2xl border ${darkMode ? 'border-slate-800 bg-slate-900/80' : 'border-slate-200 bg-white'} p-5`}>
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                  <MessageSquare size={18} />
                  <h3 className="text-lg font-semibold">AI Chat</h3>
                </div>
                {result.phase3.messages.length > 0 && (
                  <button
                    onClick={clearChatHistory}
                    className={`flex items-center gap-1 rounded-lg px-3 py-1.5 text-xs transition ${
                      darkMode ? 'bg-slate-800 text-slate-300 hover:bg-slate-700' : 'bg-slate-200 text-slate-700 hover:bg-slate-300'
                    }`}
                  >
                    <Trash2 size={12} />
                    Clear
                  </button>
                )}
              </div>

              {/* Chat messages */}
              <div className={`max-h-[500px] space-y-4 overflow-y-auto rounded-xl border p-4 ${
                darkMode ? 'border-slate-800 bg-slate-950/70' : 'border-slate-200 bg-slate-50'
              }`}>
                {result.phase3.messages.length === 0 && (
                  <div className="text-center py-8">
                    <Bot size={48} className={`mx-auto mb-3 ${darkMode ? 'text-slate-600' : 'text-slate-400'}`} />
                    <p className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>
                      Start a conversation about this repository
                    </p>
                    <p className={`mt-1 text-xs ${darkMode ? 'text-slate-500' : 'text-slate-500'}`}>
                      Ask questions about the code, architecture, or implementation
                    </p>
                  </div>
                )}

                {result.phase3.messages.map((message, index) => (
                  <div
                    key={index}
                    className={`flex gap-3 ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    {message.role === 'assistant' && (
                      <div className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-lg ${
                        darkMode ? 'bg-cyan-600' : 'bg-cyan-500'
                      }`}>
                        <Bot size={16} className="text-white" />
                      </div>
                    )}
                    <div className={`max-w-[80%] rounded-xl p-3 ${
                      message.role === 'user'
                        ? 'bg-cyan-600 text-white'
                        : darkMode ? 'bg-slate-800 text-slate-200' : 'bg-slate-200 text-slate-800'
                    }`}>
                      {message.role === 'user' ? (
                        <p className="text-sm">{message.content}</p>
                      ) : (
                        <>
                          <div className="text-sm leading-relaxed">
                            <ReactMarkdown
                              components={{
                                code({ node, inline, className, children, ...props }) {
                                  const match = /language-(\w+)/.exec(className || '');
                                  const language = match ? match[1] : 'text';
                                  return !inline && match ? (
                                    <SyntaxHighlighter
                                      style={oneDark}
                                      language={language}
                                      PreTag="div"
                                      className="rounded-lg text-xs"
                                      {...props}
                                    >
                                      {String(children).replace(/\n$/, '')}
                                    </SyntaxHighlighter>
                                  ) : (
                                    <code className={className} {...props}>
                                      {children}
                                    </code>
                                  );
                                },
                              }}
                            >
                              {message.content}
                            </ReactMarkdown>
                          </div>
                          {message.sources && message.sources.length > 0 && (
                            <div className={`mt-3 pt-3 border-t ${darkMode ? 'border-slate-700' : 'border-slate-300'}`}>
                              <p className="text-xs font-medium mb-2">Sources:</p>
                              <div className="space-y-1">
                                {message.sources.slice(0, 3).map((source, idx) => (
                                  <div key={idx} className="text-xs opacity-75">
                                    📄 {source.file} (lines {source.start_line}-{source.end_line})
                                  </div>
                                ))}
                              </div>
                            </div>
                          )}
                        </>
                      )}
                    </div>
                    {message.role === 'user' && (
                      <div className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-lg ${
                        darkMode ? 'bg-slate-700' : 'bg-slate-300'
                      }`}>
                        <User size={16} className={darkMode ? 'text-slate-200' : 'text-slate-700'} />
                      </div>
                    )}
                  </div>
                ))}

                {result.phase3.isChatLoading && (
                  <div className="flex gap-3 justify-start">
                    <div className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-lg ${
                      darkMode ? 'bg-cyan-600' : 'bg-cyan-500'
                    }`}>
                      <Bot size={16} className="text-white" />
                    </div>
                    <div className={`rounded-xl p-3 ${darkMode ? 'bg-slate-800' : 'bg-slate-200'}`}>
                      <Loader2 size={16} className="animate-spin text-cyan-500" />
                    </div>
                  </div>
                )}

                {result.phase3.chatError && (
                  <div className="rounded-xl border border-red-500 bg-red-500/10 p-3 text-sm text-red-400">
                    {result.phase3.chatError}
                  </div>
                )}
              </div>

              {/* Chat input */}
              <div className="mt-4 flex gap-2">
                <input
                  value={chatMessage}
                  onChange={(event) => setChatMessage(event.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && sendChatMessage()}
                  disabled={isChatting}
                  className={`flex-1 rounded-xl border px-4 py-3 text-sm outline-none transition ${
                    darkMode
                      ? 'border-slate-700 bg-slate-950 text-slate-100 focus:border-cyan-400'
                      : 'border-slate-300 bg-slate-50 text-slate-900 focus:border-cyan-500'
                  }`}
                  placeholder="Ask a question about the repository..."
                />
                <button
                  onClick={sendChatMessage}
                  disabled={isChatting || !chatMessage.trim()}
                  className="rounded-xl bg-cyan-600 px-4 py-3 text-sm font-medium text-white transition hover:bg-cyan-500 disabled:opacity-60"
                >
                  {isChatting ? <Loader2 size={16} className="animate-spin" /> : <Send size={16} />}
                </button>
              </div>

              {result.phase3.chatError && (
                <div className="mt-3 rounded-xl border border-red-500 bg-red-500/10 p-3 text-sm text-red-400">
                  {result.phase3.chatError}
                </div>
              )}
            </section>
          )}
        </main>
      </div>
    </div>
  );
}

export default App;