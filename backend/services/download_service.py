import os
import shutil
import tempfile
from typing import Optional

from github import Github


class DownloadService:
    def __init__(self) -> None:
        self.token = os.getenv("GITHUB_TOKEN")
        self.github_client = Github(self.token) if self.token else None
        self.cache_dir = os.path.join(tempfile.gettempdir(), "anubis-codex-cache")
        os.makedirs(self.cache_dir, exist_ok=True)

    def get_cache_path(self, owner: str, repo: str) -> str:
        return os.path.join(self.cache_dir, f"{owner}_{repo}")

    def is_cached(self, owner: str, repo: str) -> bool:
        cache_path = self.get_cache_path(owner, repo)
        if not os.path.exists(cache_path):
            return False
        # Check for actual content files (not just .git or subdirectories)
        contents = os.listdir(cache_path)
        # A valid cache has actual files at the root level
        has_files = any(os.path.isfile(os.path.join(cache_path, item)) for item in contents)
        return has_files

    def download_repository(self, owner: str, repo: str) -> str:
        cache_path = self.get_cache_path(owner, repo)

        if self.is_cached(owner, repo):
            return cache_path

        # Clean up any stale cache directory before downloading
        if os.path.exists(cache_path):
            shutil.rmtree(cache_path, ignore_errors=True)

        # Try git clone first (cross-platform using subprocess)
        try:
            import subprocess
            clone_url = f"https://github.com/{owner}/{repo}.git"
            if self.token:
                clone_url = clone_url.replace("https://", f"https://{self.token}@")
            result = subprocess.run(
                ["git", "clone", "--depth", "1", clone_url, cache_path],
                capture_output=True,
                text=True,
                timeout=60,
            )
            if result.returncode == 0 and os.path.exists(cache_path) and os.listdir(cache_path):
                return cache_path
        except Exception:
            pass

        # Fallback to ZIP download (cross-platform using zipfile)
        import requests
        import zipfile
        zip_url = f"https://github.com/{owner}/{repo}/archive/refs/heads/main.zip"
        fallback_url = f"https://github.com/{owner}/{repo}/archive/refs/heads/master.zip"

        for url in [zip_url, fallback_url]:
            try:
                os.makedirs(cache_path, exist_ok=True)
                response = requests.get(url, timeout=60, stream=True)
                if response.ok:
                    zip_path = os.path.join(cache_path, "repo.zip")
                    with open(zip_path, "wb") as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                    
                    # Extract using Python's zipfile (cross-platform)
                    with zipfile.ZipFile(zip_path, 'r') as zf:
                        zf.extractall(cache_path)
                    os.remove(zip_path)
                    
                    # Move extracted contents to root
                    # Filter out .git and other non-content directories
                    extracted_dirs = [d for d in os.listdir(cache_path)
                                      if os.path.isdir(os.path.join(cache_path, d))
                                      and d not in (".git", "objects", "refs", "hooks", "info")
                                      and not d.startswith(".")]
                    if extracted_dirs:
                        subdir = os.path.join(cache_path, extracted_dirs[0])
                        for item in os.listdir(subdir):
                            shutil.move(os.path.join(subdir, item), cache_path)
                        os.rmdir(subdir)
                        return cache_path
            except Exception:
                continue

        raise RuntimeError(f"Failed to download repository {owner}/{repo}")

    def clear_cache(self, owner: str, repo: str) -> None:
        cache_path = self.get_cache_path(owner, repo)
        if os.path.exists(cache_path):
            shutil.rmtree(cache_path, ignore_errors=True)

    def clear_all_cache(self) -> None:
        if os.path.exists(self.cache_dir):
            shutil.rmtree(self.cache_dir, ignore_errors=True)
            os.makedirs(self.cache_dir, exist_ok=True)