import { useState, useMemo, useCallback } from 'react';
import {
  ChevronDown,
  ChevronRight,
  FileText,
  Folder,
  FolderOpen,
  Search,
} from 'lucide-react';
import { getLanguageColor, getLanguageDisplayName } from '../utils/languageUtils';

/**
 * FileExplorer - Professional file tree with expand/collapse, icons, search, and hover effects.
 */
const FileExplorer = ({ tree, files, onFileSelect, selectedFile }) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [expandedNodes, setExpandedNodes] = useState(new Set());

  // Filter files based on search query
  const filteredFiles = useMemo(() => {
    if (!searchQuery.trim()) return files || [];
    const q = searchQuery.toLowerCase();
    return (files || []).filter((file) =>
      file.path.toLowerCase().includes(q)
    );
  }, [files, searchQuery]);

  // Toggle a node's expanded state
  const toggleNode = useCallback((path) => {
    setExpandedNodes((prev) => {
      const next = new Set(prev);
      if (next.has(path)) {
        next.delete(path);
      } else {
        next.add(path);
      }
      return next;
    });
  }, []);

  // Expand all nodes
  const expandAll = useCallback(() => {
    const allPaths = new Set();
    const collectPaths = (node, prefix = '') => {
      if (!node || typeof node !== 'object') return;
      for (const [key, value] of Object.entries(node)) {
        const path = prefix ? `${prefix}/${key}` : key;
        if (value && typeof value === 'object' && !value.path) {
          allPaths.add(path);
          collectPaths(value, path);
        }
      }
    };
    collectPaths(tree);
    setExpandedNodes(allPaths);
  }, [tree]);

  // Collapse all nodes
  const collapseAll = useCallback(() => {
    setExpandedNodes(new Set());
  }, []);

  // Check if a file is selected
  const isFileSelected = (file) => {
    return selectedFile?.path === file.path;
  };

  // Render a tree node (directory or file)
  const renderTreeNode = (node, name, path, depth = 0) => {
    // Check if this is a file (has 'path' property) or a directory
    const isFile = node && typeof node === 'object' && node.path;

    if (isFile) {
      const file = node;
      const isSelected = isFileSelected(file);
      const language = file.language || 'text';

      return (
        <div
          key={path}
          className={`file-tree-item ${isSelected ? 'active' : ''}`}
          style={{ paddingLeft: `${depth * 0.75 + 0.375}rem` }}
          onClick={() => onFileSelect(file)}
        >
          <FileText size={14} className="file-icon" />
          <span className="file-name" title={file.path}>
            {file.name}
          </span>
          {language && language !== 'text' && (
            <span
              className="file-lang-dot"
              title={getLanguageDisplayName(language)}
              style={{ backgroundColor: getLanguageColor(language) }}
            />
          )}
        </div>
      );
    }

    // It's a directory
    const isExpanded = expandedNodes.has(path);
    const hasChildren = node && Object.keys(node).length > 0;

    return (
      <div key={path}>
        <div
          className="file-tree-item"
          style={{ paddingLeft: `${depth * 0.75 + 0.375}rem` }}
          onClick={() => toggleNode(path)}
        >
          {hasChildren ? (
            isExpanded ? (
              <ChevronDown size={14} className="text-tertiary" />
            ) : (
              <ChevronRight size={14} className="text-tertiary" />
            )
          ) : (
            <span style={{ width: '0.875rem' }} />
          )}
          {isExpanded ? (
            <FolderOpen size={14} className="file-icon text-accent" />
          ) : (
            <Folder size={14} className="file-icon text-tertiary" />
          )}
          <span className="text-secondary font-medium">{name}</span>
        </div>

        {isExpanded && hasChildren && (
          <div>
            {Object.entries(node).map(([childName, childNode]) => {
              const childPath = path ? `${path}/${childName}` : childName;
              return renderTreeNode(childNode, childName, childPath, depth + 1);
            })}
          </div>
        )}
      </div>
    );
  };

  // Render search results (flat list)
  const renderSearchResults = () => {
    if (filteredFiles.length === 0) {
      return (
        <div className="empty-state">
          No files found.
        </div>
      );
    }

    return (
      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
        {filteredFiles.map((file) => {
          const isSelected = isFileSelected(file);
          const language = file.language || 'text';
          return (
            <div
              key={file.path}
              className={`file-search-result ${isSelected ? 'active' : ''}`}
              onClick={() => onFileSelect(file)}
            >
              <FileText size={14} className="file-icon" />
              <span className="file-name" title={file.path}>
                {file.name}
              </span>
              <span className="file-path">{file.path}</span>
              {language && language !== 'text' && (
                <span
                  className="file-lang-dot"
                  title={getLanguageDisplayName(language)}
                  style={{ backgroundColor: getLanguageColor(language) }}
                />
              )}
            </div>
          );
        })}
      </div>
    );
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      {/* Search */}
      <div className="file-tree-search">
        <div className="input-wrapper">
          <span className="input-icon">
            <Search size={14} />
          </span>
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search files..."
            className="input-field"
          />
        </div>
      </div>

      {/* Tree / Search Results */}
      <div className="file-tree">
        {searchQuery.trim() ? (
          renderSearchResults()
        ) : tree && Object.keys(tree).length > 0 ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.125rem' }}>
            {Object.entries(tree).map(([name, node]) =>
              renderTreeNode(node, name, name, 0)
            )}
          </div>
        ) : (
          <div className="empty-state">
            <div className="empty-state-icon">
              <FileText size={24} />
              <p>No files available</p>
            </div>
          </div>
        )}
      </div>

      {/* Footer actions */}
      {tree && Object.keys(tree).length > 0 && !searchQuery.trim() && (
        <div className="file-tree-footer">
          <button
            onClick={expandAll}
            className="file-tree-action"
          >
            Expand All
          </button>
          <span className="file-tree-separator">•</span>
          <button
            onClick={collapseAll}
            className="file-tree-action"
          >
            Collapse All
          </button>
        </div>
      )}
    </div>
  );
};

export default FileExplorer;