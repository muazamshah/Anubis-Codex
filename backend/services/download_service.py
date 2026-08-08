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
        return os.path.exists(cache_path) and os.listdir(cache_path)

    def download_repository(self, owner: str, repo: str) -> str:
        cache_path = self.get_cache_path(owner, repo)

        if self.is_cached(owner, repo):
            return cache_path

        if self.github_client:
            try:
                repository = self.github_client.get_repo(f"{owner}/{repo}")
                clone_url = repository.clone_url
                if self.token:
                    clone_url = clone_url.replace("https://", f"https://{self.token}@")

                os.makedirs(cache_path, exist_ok=True)
                os.system(f"git clone --depth 1 {clone_url} {cache_path} 2>/dev/null")
                if os.listdir(cache_path):
                    return cache_path
            except Exception:
                pass

        # Fallback to ZIP download
        zip_url = f"https://github.com/{owner}/{repo}/archive/refs/heads/main.zip"
        fallback_url = f"https://github.com/{owner}/{repo}/archive/refs/heads/master.zip"

        import requests
        for url in [zip_url, fallback_url]:
            try:
                response = requests.get(url, timeout=30, stream=True)
                if response.ok:
                    zip_path = os.path.join(cache_path, "repo.zip")
                    with open(zip_path, "wb") as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                    os.system(f"cd {cache_path} && unzip -q repo.zip && rm repo.zip")
                    extracted = os.listdir(cache_path)
                    if extracted:
                        subdir = os.path.join(cache_path, extracted[0])
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