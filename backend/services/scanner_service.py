import os
from typing import Any, Dict, List

IGNORED_DIRECTORIES = {
    ".git",
    "node_modules",
    "dist",
    "build",
    "venv",
    "__pycache__",
    ".venv",
    "target",
    "bin",
    "obj",
}
IGNORED_FILES = {"package-lock.json", "yarn.lock", ".DS_Store", "Thumbs.db"}

SUPPORTED_EXTENSIONS = {
    ".py": "python",
    ".js": "javascript",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".jsx": "javascript",
    ".cpp": "cpp",
    ".cc": "cpp",
    ".cxx": "cpp",
    ".java": "java",
    ".go": "go",
    ".rs": "rust",
    ".md": "markdown",
}

# Extensionless files that should be scanned
EXTENSIONLESS_FILES = {
    "readme": "markdown",
    "license": "markdown",
    "makefile": "makefile",
    "dockerfile": "dockerfile",
    "contributing": "markdown",
    "changelog": "markdown",
}


class ScannerService:
    def scan_repository(self, root_path: str) -> Dict[str, Any]:
        files = self._collect_files(root_path)
        languages = self._detect_languages(files)
        return {
            "files": files,
            "count": len(files),
            "languages": languages,
            "tree": self._build_tree(root_path, files),
        }

    def _collect_files(self, root_path: str) -> List[Dict[str, Any]]:
        files: List[Dict[str, Any]] = []
        for current_root, dirs, filenames in os.walk(root_path):
            dirs[:] = [d for d in dirs if d not in IGNORED_DIRECTORIES]
            for filename in filenames:
                if filename in IGNORED_FILES:
                    continue
                extension = os.path.splitext(filename)[1].lower()
                if extension not in SUPPORTED_EXTENSIONS:
                    # Handle extensionless files (README, LICENSE, Makefile, etc.)
                    if filename.lower() in EXTENSIONLESS_FILES:
                        language = EXTENSIONLESS_FILES[filename.lower()]
                    else:
                        continue
                else:
                    language = SUPPORTED_EXTENSIONS[extension]
                file_path = os.path.join(current_root, filename)
                relative_path = os.path.relpath(file_path, root_path)
                files.append(
                    {
                        "path": relative_path,
                        "name": filename,
                        "language": language,
                        "size": os.path.getsize(file_path),
                    }
                )
        return files

    def read_file_content(self, root_path: str, file_path: str) -> str:
        """Read the content of a file."""
        try:
            full_path = os.path.join(root_path, file_path)
            with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        except Exception:
            return ""

    def scan_repository_with_content(self, root_path: str, max_file_size: int = 100000) -> Dict[str, Any]:
        """
        Scan repository and include file contents.

        Args:
            root_path: Root directory of the repository
            max_file_size: Maximum file size to read (in bytes), default 100KB
        """
        files = self._collect_files(root_path)
        languages = self._detect_languages(files)

        # Read file contents
        files_with_content = []
        for file_info in files:
            file_content = ""
            if file_info["size"] <= max_file_size:
                file_content = self.read_file_content(root_path, file_info["path"])

            files_with_content.append({
                **file_info,
                "content": file_content,
            })

        return {
            "files": files_with_content,
            "count": len(files_with_content),
            "languages": languages,
            "tree": self._build_tree(root_path, files),
        }

    def _detect_languages(self, files: List[Dict[str, Any]]) -> List[str]:
        languages = sorted({entry["language"] for entry in files})
        return languages

    def _build_tree(self, root_path: str, files: List[Dict[str, Any]]) -> Dict[str, Any]:
        tree = {}
        for file in files:
            parts = file["path"].split(os.sep)
            current = tree
            for part in parts[:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]
            current[parts[-1]] = file
        return tree
