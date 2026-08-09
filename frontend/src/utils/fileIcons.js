/**
 * File icon and language utilities for the Anubis Codex file explorer.
 */

// Map of file extensions to language identifiers
export const EXTENSION_LANGUAGE_MAP = {
  '.py': 'python',
  '.js': 'javascript',
  '.jsx': 'javascript',
  '.ts': 'typescript',
  '.tsx': 'typescript',
  '.cpp': 'cpp',
  '.cc': 'cpp',
  '.cxx': 'cpp',
  '.c': 'c',
  '.h': 'c',
  '.hpp': 'cpp',
  '.java': 'java',
  '.go': 'go',
  '.rs': 'rust',
  '.md': 'markdown',
  '.json': 'json',
  '.yaml': 'yaml',
  '.yml': 'yaml',
  '.toml': 'toml',
  '.ini': 'ini',
  '.cfg': 'ini',
  '.html': 'html',
  '.css': 'css',
  '.scss': 'scss',
  '.sass': 'sass',
  '.less': 'less',
  '.sql': 'sql',
  '.sh': 'bash',
  '.bash': 'bash',
  '.zsh': 'bash',
  '.ps1': 'powershell',
  '.dockerfile': 'dockerfile',
  '.makefile': 'makefile',
  '.rb': 'ruby',
  '.php': 'php',
  '.swift': 'swift',
  '.kt': 'kotlin',
  '.scala': 'scala',
  '.r': 'r',
  '.R': 'r',
  '.lua': 'lua',
  '.vim': 'vim',
  '.tex': 'latex',
  '.xml': 'xml',
  '.csv': 'csv',
  '.txt': 'text',
};

// Map of language identifiers to display names
export const LANGUAGE_NAMES = {
  python: 'Python',
  javascript: 'JavaScript',
  typescript: 'TypeScript',
  cpp: 'C++',
  c: 'C',
  java: 'Java',
  go: 'Go',
  rust: 'Rust',
  markdown: 'Markdown',
  json: 'JSON',
  yaml: 'YAML',
  toml: 'TOML',
  ini: 'INI',
  html: 'HTML',
  css: 'CSS',
  scss: 'SCSS',
  sass: 'Sass',
  less: 'Less',
  sql: 'SQL',
  bash: 'Shell',
  powershell: 'PowerShell',
  dockerfile: 'Dockerfile',
  makefile: 'Makefile',
  ruby: 'Ruby',
  php: 'PHP',
  swift: 'Swift',
  kotlin: 'Kotlin',
  scala: 'Scala',
  r: 'R',
  lua: 'Lua',
  vim: 'Vim',
  latex: 'LaTeX',
  xml: 'XML',
  csv: 'CSV',
  text: 'Text',
};

// Language to syntax highlighter language mapping
export const LANGUAGE_TO_HIGHLIGHT = {
  python: 'python',
  javascript: 'javascript',
  typescript: 'typescript',
  cpp: 'cpp',
  c: 'c',
  java: 'java',
  go: 'go',
  rust: 'rust',
  markdown: 'markdown',
  json: 'json',
  yaml: 'yaml',
  toml: 'toml',
  ini: 'ini',
  html: 'html',
  css: 'css',
  scss: 'scss',
  sass: 'sass',
  less: 'less',
  sql: 'sql',
  bash: 'bash',
  powershell: 'powershell',
  dockerfile: 'dockerfile',
  makefile: 'makefile',
  ruby: 'ruby',
  php: 'php',
  swift: 'swift',
  kotlin: 'kotlin',
  scala: 'scala',
  r: 'r',
  lua: 'lua',
  vim: 'vim',
  latex: 'latex',
  xml: 'xml',
  csv: 'csv',
  text: 'text',
};

// Language to color mapping (for badges/indicators)
export const LANGUAGE_COLORS = {
  python: '#306998',
  javascript: '#f7df1e',
  typescript: '#3178c6',
  cpp: '#f34b7d',
  c: '#a8b9cc',
  java: '#b07219',
  go: '#00add8',
  rust: '#f74c00',
  markdown: '#083fa1',
  json: '#68a538',
  yaml: '#40a87c',
  toml: '#67c587',
  ini: '#517866',
  html: '#e34c26',
  css: '#563d7c',
  scss: '#c65383',
  sass: '#6e4549',
  less: '#1c87c9',
  sql: '#f29111',
  bash: '#47a649',
  powershell: '#0193b0',
  dockerfile: '#38434a',
  makefile: '#513960',
  ruby: '#cc342b',
  php: '#6140c2',
  swift: '#f05032',
  kotlin: '#7463a3',
  scala: '#c27d22',
  r: '#1980fa',
  lua: '#000080',
  vim: '#019833',
  latex: '#51ca8f',
  xml: '#0060ac',
  csv: '#437',
  text: '#707070',
};

// Get the display name for a language
export const getLanguageName = (language) => {
  if (!language) return 'Unknown';
  return LANGUAGE_NAMES[language.toLowerCase()] || language;
};

// Get the color for a language
export const getLanguageColor = (language) => {
  if (!language) return '#707070';
  return LANGUAGE_COLORS[language.toLowerCase()] || '#707070';
};

// Get the syntax highlighter language
export const getHighlightLanguage = (language) => {
  if (!language) return 'text';
  return LANGUAGE_TO_HIGHLIGHT[language.toLowerCase()] || 'text';
};

// Get file extension from filename
export const getFileExtension = (filename) => {
  const lastDot = filename.lastIndexOf('.');
  if (lastDot <= 0) return '';
  return filename.slice(lastDot).toLowerCase();
};

// Get language from filename
export const getLanguageFromFilename = (filename) => {
  const ext = getFileExtension(filename);
  if (ext && EXTENSION_LANGUAGE_MAP[ext]) {
    return EXTENSION_LANGUAGE_MAP[ext];
  }
  // Handle extensionless files
  const lower = filename.toLowerCase();
  if (lower === 'readme' || lower === 'license' || lower === 'contributing' || lower === 'changelog') {
    return 'markdown';
  }
  if (lower === 'makefile') return 'makefile';
  if (lower === 'dockerfile') return 'dockerfile';
  return 'text';
};
