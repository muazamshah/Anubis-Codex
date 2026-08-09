/**
 * Language utility functions for Anubis Codex.
 */

// Map of language identifiers to their display names
export const LANGUAGE_DISPLAY_NAMES = {
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
  sql: 'SQL',
  bash: 'Shell',
  dockerfile: 'Dockerfile',
  makefile: 'Makefile',
  ruby: 'Ruby',
  php: 'PHP',
  swift: 'Swift',
  kotlin: 'Kotlin',
  scala: 'Scala',
  r: 'R',
  lua: 'Lua',
  xml: 'XML',
  csv: 'CSV',
  text: 'Text',
};

// Get display name for a language
export const getLanguageDisplayName = (language) => {
  if (!language) return 'Unknown';
  return LANGUAGE_DISPLAY_NAMES[language.toLowerCase()] || language;
};

// Get the primary language from a list of languages
export const getPrimaryLanguage = (languages) => {
  if (!languages || languages.length === 0) return null;
  return languages[0];
};

// Format languages for display
export const formatLanguages = (languages) => {
  if (!languages || languages.length === 0) return 'Unknown';
  return languages.map(getLanguageDisplayName).join(', ');
};

// Get file size in human-readable format
export const formatFileSize = (bytes) => {
  if (!bytes || bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
};

// Get color for a language (for badges and indicators)
export const getLanguageColor = (language) => {
  if (!language) return 'rgb(110, 120, 145)';
  
  const lang = language.toLowerCase();
  const colors = {
    python: 'rgb(55, 118, 171)',
    javascript: 'rgb(241, 224, 90)',
    typescript: 'rgb(49, 120, 198)',
    cpp: 'rgb(0, 89, 156)',
    c: 'rgb(0, 89, 156)',
    java: 'rgb(176, 114, 25)',
    go: 'rgb(0, 173, 216)',
    rust: 'rgb(222, 165, 132)',
    markdown: 'rgb(23, 162, 184)',
    json: 'rgb(255, 206, 84)',
    yaml: 'rgb(255, 206, 84)',
    html: 'rgb(227, 79, 38)',
    css: 'rgb(38, 77, 228)',
    scss: 'rgb(204, 102, 153)',
    sql: 'rgb(0, 0, 255)',
    bash: 'rgb(137, 224, 81)',
    dockerfile: 'rgb(36, 150, 237)',
    ruby: 'rgb(204, 52, 45)',
    php: 'rgb(119, 123, 180)',
    swift: 'rgb(255, 148, 0)',
    kotlin: 'rgb(127, 82, 242)',
    scala: 'rgb(204, 57, 43)',
    r: 'rgb(25, 114, 120)',
    lua: 'rgb(0, 0, 128)',
    xml: 'rgb(255, 206, 84)',
  };
  
  return colors[lang] || 'rgb(110, 120, 145)';
};

// Get syntax highlighting language for code blocks
export const getHighlightLanguage = (language) => {
  if (!language) return 'text';
  
  const lang = language.toLowerCase();
  const mapping = {
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
    html: 'html',
    css: 'css',
    scss: 'scss',
    sql: 'sql',
    bash: 'bash',
    shell: 'bash',
    dockerfile: 'dockerfile',
    ruby: 'ruby',
    php: 'php',
    swift: 'swift',
    kotlin: 'kotlin',
    scala: 'scala',
    r: 'r',
    lua: 'lua',
    xml: 'xml',
  };
  
  return mapping[lang] || 'text';
};

// Get file icon name based on file name and language
export const getFileIconName = (fileName, language) => {
  const lower = fileName.toLowerCase();

  // Special files
  if (lower === 'package.json') return 'Package';
  if (lower === 'requirements.txt') return 'Requirements';
  if (lower === 'dockerfile' || lower === 'dockerfile') return 'Docker';
  if (lower === 'makefile') return 'Make';
  if (lower === 'readme.md' || lower === 'readme') return 'Markdown';
  if (lower === 'license' || lower === 'license.md') return 'License';
  if (lower === 'contributing.md') return 'Markdown';
  if (lower === 'yarn.lock') return 'Yarn';
  if (lower === 'pnpm-lock.yaml') return 'Yaml';
  if (lower === 'tsconfig.json') return 'Typescript';
  if (lower === 'next.config.js' || lower === 'next.config.mjs') return 'Next';
  if (lower === 'vite.config.js' || lower === 'vite.config.ts') return 'Vite';
  if (lower === 'tailwind.config.js' || lower === 'tailwind.config.ts') return 'Tailwind';
  if (lower === 'postcss.config.js') return 'Postcss';

  // By language
  if (language) {
    const lang = language.toLowerCase();
    if (lang === 'python') return 'Python';
    if (lang === 'javascript') return 'Javascript';
    if (lang === 'typescript') return 'Typescript';
    if (lang === 'cpp') return 'Cpp';
    if (lang === 'c') return 'C';
    if (lang === 'java') return 'Java';
    if (lang === 'go') return 'Go';
    if (lang === 'rust') return 'Rust';
    if (lang === 'markdown') return 'Markdown';
    if (lang === 'json') return 'Json';
    if (lang === 'yaml') return 'Yaml';
    if (lang === 'html') return 'Html';
    if (lang === 'css') return 'Css';
    if (lang === 'scss') return 'Scss';
    if (lang === 'sql') return 'Sql';
    if (lang === 'bash') return 'Shell';
    if (lang === 'dockerfile') return 'Docker';
    if (lang === 'makefile') return 'Make';
    if (lang === 'ruby') return 'Ruby';
    if (lang === 'php') return 'Php';
    if (lang === 'swift') return 'Swift';
    if (lang === 'kotlin') return 'Kotlin';
    if (lang === 'scala') return 'Scala';
    if (lang === 'r') return 'R';
    if (lang === 'lua') return 'Lua';
    if (lang === 'xml') return 'Xml';
    if (lang === 'csv') return 'Csv';
  }

  // By extension
  const ext = lower.split('.').pop();
  const extIcons = {
    py: 'Python',
    js: 'Javascript',
    jsx: 'Javascript',
    ts: 'Typescript',
    tsx: 'Typescript',
    cpp: 'Cpp',
    cc: 'Cpp',
    c: 'C',
    h: 'C',
    java: 'Java',
    go: 'Go',
    rs: 'Rust',
    md: 'Markdown',
    json: 'Json',
    yaml: 'Yaml',
    yml: 'Yaml',
    toml: 'Toml',
    ini: 'Ini',
    html: 'Html',
    htm: 'Html',
    css: 'Css',
    scss: 'Scss',
    sass: 'Sass',
    less: 'Less',
    sql: 'Sql',
    sh: 'Shell',
    bash: 'Shell',
    ps1: 'Powershell',
    rb: 'Ruby',
    php: 'Php',
    swift: 'Swift',
    kt: 'Kotlin',
    scala: 'Scala',
    r: 'R',
    lua: 'Lua',
    vim: 'Vim',
    tex: 'Latex',
    xml: 'Xml',
    csv: 'Csv',
    txt: 'Text',
  };

  return extIcons[ext] || 'FileText';
};
