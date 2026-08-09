import { useCallback, useEffect, useMemo, useState, useRef } from 'react';
import {
  Code,
  FileCode,
  FileText,
  MessageSquare,
  Search,
  X,
} from 'lucide-react';
import Header from './components/Header';
import LandingScreen from './components/LandingScreen';
import AnalysisProgress from './components/AnalysisProgress';
import RepositoryHeader from './components/RepositoryHeader';
import FileExplorer from './components/FileExplorer';
import RepositoryInfo from './components/RepositoryInfo';
import ChatInterface from './components/ChatInterface';
import FilePreview from './components/FilePreview';
import ReadmeViewer from './components/ReadmeViewer';
import SearchResults from './components/SearchResults';
import StatusIndicator from './components/common/StatusIndicator';
import { getLanguageColor, getLanguageDisplayName } from './utils/languageUtils';

const API_BASE = import.meta.env.VITE_API_BASE || '';

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
  indexing: {
    chunks_created: 0,
    embeddings_generated: 0,
    vector_db_updated: false,
  },
};

function App() {
  const [url, setUrl] = useState('');
  const [result, setResult] = useState(initialState);
  const [loading, setLoading] = useState(false);
  const [darkMode, setDarkMode] = useState(true);
  const [selectedFile, setSelectedFile] = useState(null);
  const [activeView, setActiveView] = useState('chat'); // 'chat', 'files', 'readme'
  const [searchText, setSearchText] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [isSearching, setIsSearching] = useState(false);
  const [chatMessage, setChatMessage] = useState('');
  const [isChatting, setIsChatting] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [chatError, setChatError] = useState(null);
  const [leftSidebarOpen, setLeftSidebarOpen] = useState(false);
  const [rightSidebarOpen, setRightSidebarOpen] = useState(false);
  const [analysisProgress, setAnalysisProgress] = useState(0);
  const progressIntervalRef = useRef(null);

  // Apply theme
  useEffect(() => {
    const theme = darkMode ? 'dark' : 'light';
    document.documentElement.setAttribute('data-theme', theme);
    document.body.classList.toggle('dark', darkMode);
  }, [darkMode]);

  // Cleanup progress interval on unmount
  useEffect(() => {
    return () => {
      if (progressIntervalRef.current) {
        clearInterval(progressIntervalRef.current);
      }
    };
  }, []);

  // Derived state
  const isIndexed =
    result.indexing?.chunks_created > 0 || result.indexing?.vector_db_updated;

  const isRepoLoaded = result.status === 'completed' && result.repository;

  // Find file content from the files array
  const findFileContent = useCallback(
    (file) => {
      if (!file) return null;
      // If the file already has content, use it
      if (file.content) return file;
      // Otherwise, search the files array
      const found = result.files?.find((f) => f.path === file.path);
      return found || file;
    },
    [result.files]
  );

  // Handle file selection
  const handleFileSelect = useCallback(
    (file) => {
      const fileWithContent = findFileContent(file);
      setSelectedFile(fileWithContent);
      setActiveView('files');
    },
    [findFileContent]
  );

  // Handle source click from chat
  const handleSourceClick = useCallback(
    (filePath, startLine, endLine) => {
      const file = result.files?.find((f) => f.path === filePath);
      if (file) {
        handleFileSelect(file);
      }
    },
    [result.files, handleFileSelect]
  );

  // Handle quick question
  const handleQuickQuestion = useCallback(
    (question) => {
      setChatMessage(question);
      // Auto-send the question
      setTimeout(() => {
        const event = new Event('quick-question');
        window.dispatchEvent(event);
      }, 100);
    },
    []
  );

  // Send chat message
  const sendChatMessage = useCallback(async () => {
    if (!chatMessage.trim() || !result.repository || isChatting) return;

    const repository_id = result.repository.full_name;
    const messageToSend = chatMessage;

    // Create session if needed
    let currentSessionId = sessionId;
    if (!currentSessionId) {
      try {
        const sessionResponse = await fetch(`${API_BASE}/api/session/create`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ repository_id }),
        });
        const sessionData = await sessionResponse.json();
        if (sessionData.status === 'completed') {
          currentSessionId = sessionData.session.session_id;
          setSessionId(currentSessionId);
        }
      } catch (error) {
        console.error('Session creation failed:', error);
      }
    }

    const userMessage = {
      role: 'user',
      content: messageToSend,
      timestamp: Date.now(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setChatMessage('');
    setIsChatting(true);
    setChatError(null);

    try {
      const response = await fetch(`${API_BASE}/api/repository/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: currentSessionId || `session_${Date.now()}`,
          question: messageToSend,
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

      setMessages((prev) => [...prev, assistantMessage]);
      if (data.session_id) {
        setSessionId(data.session_id);
      }
    } catch (error) {
      setChatError(`Chat failed: ${error.message}`);
    } finally {
      setIsChatting(false);
    }
  }, [chatMessage, result.repository, isChatting, sessionId]);

  // Clear chat history
  const clearChatHistory = useCallback(async () => {
    if (!sessionId) {
      setMessages([]);
      return;
    }

    try {
      await fetch(`${API_BASE}/api/history/clear?session_id=${sessionId}`, {
        method: 'DELETE',
      });
    } catch (error) {
      console.error('Failed to clear history:', error);
    }
    setMessages([]);
  }, [sessionId]);

  // Search repository
  const searchRepository = useCallback(async () => {
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
  }, [searchText]);

  // Analyze repository
  const analyzeRepository = useCallback(async () => {
    if (!url.trim()) return;

    setLoading(true);
    setResult(initialState);
    setSelectedFile(null);
    setActiveView('chat');
    setMessages([]);
    setSessionId(null);
    setChatError(null);
    setSearchResults([]);
    setSearchText('');
    setAnalysisProgress(0);

    // Start progress simulation
    progressIntervalRef.current = setInterval(() => {
      setAnalysisProgress((prev) => {
        if (prev >= 90) return prev;
        return prev + Math.random() * 8;
      });
    }, 300);

    try {
      const response = await fetch(`${API_BASE}/api/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url }),
      });

      if (!response.ok) throw new Error('Analysis failed');
      const data = await response.json();

      setAnalysisProgress(100);

      setResult({
        status: data.status,
        repository: data.repository,
        metadata: data.metadata,
        files: data.files || [],
        fileCount: data.file_count || 0,
        languages: data.languages || [],
        tree: data.tree || {},
        selectedFile: null,
        error: null,
        indexing: {
          chunks_created: data.indexing?.chunks_created || 0,
          embeddings_generated: data.indexing?.embeddings_generated || 0,
          vector_db_updated: data.indexing?.vector_db_updated || false,
        },
      });
    } catch (error) {
      setAnalysisProgress(0);
      setResult((current) => ({
        ...current,
        status: 'error',
        error: `Analysis failed: ${error.message}`,
      }));
    } finally {
      setLoading(false);
      if (progressIntervalRef.current) {
        clearInterval(progressIntervalRef.current);
      }
    }
  }, [url]);

  // Handle quick question send
  useEffect(() => {
    const handler = () => {
      if (chatMessage.trim() && !isChatting) {
        sendChatMessage();
      }
    };
    window.addEventListener('quick-question', handler);
    return () => window.removeEventListener('quick-question', handler);
  }, [chatMessage, isChatting, sendChatMessage]);

  // Toggle theme
  const toggleTheme = () => {
    setDarkMode((v) => !v);
  };

  // Render the appropriate view
  const renderMainContent = () => {
    if (!isRepoLoaded) {
      return null;
    }

    return (
      <div className="workspace">
        {/* Left Sidebar - Navigation & File Explorer */}
        <div className="sidebar sidebar-left">
          {/* Navigation */}
          <div className="sidebar-nav">
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.125rem' }}>
              <button
                onClick={() => setActiveView('chat')}
                className={`nav-item ${activeView === 'chat' ? 'active' : ''}`}
              >
                <MessageSquare size={16} />
                <span>AI Chat</span>
              </button>
              <button
                onClick={() => setActiveView('files')}
                className={`nav-item ${activeView === 'files' ? 'active' : ''}`}
              >
                <FileCode size={16} />
                <span>Files</span>
              </button>
              <button
                onClick={() => setActiveView('readme')}
                className={`nav-item ${activeView === 'readme' ? 'active' : ''}`}
              >
                <FileText size={16} />
                <span>README</span>
              </button>
            </div>
          </div>

          {/* File Explorer */}
          <div style={{ flex: 1, overflow: 'hidden' }}>
            <FileExplorer
              tree={result.tree}
              files={result.files}
              onFileSelect={handleFileSelect}
              selectedFile={selectedFile}
            />
          </div>

          {/* Repository Info Footer */}
          <div className="sidebar-footer">
            <div className="sidebar-footer-row">
              <span className="sidebar-footer-label">Status</span>
              <StatusIndicator
                status={isIndexed ? 'completed' : 'idle'}
                label={isIndexed ? 'Indexed' : 'Not Indexed'}
                showDot={true}
                size="sm"
              />
            </div>
            <div className="sidebar-footer-row">
              <span className="sidebar-footer-label">Files</span>
              <span className="sidebar-footer-value">{result.fileCount}</span>
            </div>
            {result.languages.length > 0 && (
              <div className="sidebar-lang-dots">
                {result.languages.slice(0, 3).map((lang) => (
                  <span
                    key={lang}
                    className="lang-dot"
                    style={{ backgroundColor: getLanguageColor(lang) }}
                    title={getLanguageDisplayName(lang)}
                  />
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Center - Main Content */}
        <div className="center-panel">
          {activeView === 'chat' && (
            <ChatInterface
              messages={messages}
              isChatLoading={isChatting}
              chatError={chatError}
              chatMessage={chatMessage}
              onChatMessageChange={setChatMessage}
              onSendMessage={sendChatMessage}
              onClearChat={clearChatHistory}
              onQuickQuestion={handleQuickQuestion}
              onSourceClick={handleSourceClick}
              isIndexed={isIndexed}
            />
          )}
          {activeView === 'files' && selectedFile && (
            <FilePreview
              file={selectedFile}
              onClose={() => setActiveView('chat')}
              darkMode={darkMode}
            />
          )}
          {activeView === 'readme' && result.metadata?.readme && (
            <ReadmeViewer
              readme={result.metadata.readme}
              onClose={() => setActiveView('chat')}
            />
          )}
        </div>

        {/* Right Sidebar - Repository Info */}
        <div className="sidebar sidebar-right">
          <RepositoryInfo
            repository={result.repository}
            metadata={result.metadata}
            fileCount={result.fileCount}
            languages={result.languages}
            indexing={result.indexing}
            vectorStats={null}
            cacheStats={null}
            onQuickQuestion={handleQuickQuestion}
            onSearch={searchRepository}
            searchText={searchText}
            onSearchTextChange={setSearchText}
            searchResults={searchResults}
            isSearching={isSearching}
            isIndexed={isIndexed}
          />
        </div>
      </div>
    );
  };

  return (
    <div className="app-shell" data-theme={darkMode ? 'dark' : 'light'}>
      {/* Header */}
      <Header
        darkMode={darkMode}
        onToggleTheme={toggleTheme}
        showMenuButton={isRepoLoaded}
        onMenuClick={() => setLeftSidebarOpen(true)}
        repository={result.repository}
      />

      {/* Main content */}
      <main className="main-content">
        {loading && (
          <AnalysisProgress url={url} progress={analysisProgress} />
        )}

        {!loading && !isRepoLoaded && (
          <LandingScreen
            url={url}
            onUrlChange={setUrl}
            onAnalyze={analyzeRepository}
            loading={loading}
            error={result.error}
          />
        )}

        {!loading && isRepoLoaded && renderMainContent()}
      </main>

      {/* Mobile sidebar overlays */}
      {leftSidebarOpen && isRepoLoaded && (
        <div
          className="drawer-overlay left"
          onClick={() => setLeftSidebarOpen(false)}
        >
          <div
            className="drawer-panel left"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="drawer-header">
              <h3 className="drawer-title">
                File Explorer
              </h3>
              <button
                onClick={() => setLeftSidebarOpen(false)}
                className="icon-btn"
              >
                <X size={16} />
              </button>
            </div>
            <div className="drawer-body">
              <FileExplorer
                tree={result.tree}
                files={result.files}
                onFileSelect={(file) => {
                  handleFileSelect(file);
                  setLeftSidebarOpen(false);
                }}
                selectedFile={selectedFile}
              />
            </div>
          </div>
        </div>
      )}

      {rightSidebarOpen && isRepoLoaded && (
        <div
          className="drawer-overlay right"
          onClick={() => setRightSidebarOpen(false)}
        >
          <div
            className="drawer-panel right"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="drawer-header">
              <h3 className="drawer-title">
                Repository Info
              </h3>
              <button
                onClick={() => setRightSidebarOpen(false)}
                className="icon-btn"
              >
                <X size={16} />
              </button>
            </div>
            <div className="drawer-body">
              <RepositoryInfo
                repository={result.repository}
                metadata={result.metadata}
                fileCount={result.fileCount}
                languages={result.languages}
                indexing={result.indexing}
                vectorStats={null}
                cacheStats={null}
                onQuickQuestion={handleQuickQuestion}
                onSearch={searchRepository}
                searchText={searchText}
                onSearchTextChange={setSearchText}
                searchResults={searchResults}
                isSearching={isSearching}
                isIndexed={isIndexed}
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;

