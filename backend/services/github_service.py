import os
import re
from typing import Any, Dict, List

import requests

try:
    from github import Github
except Exception:  # pragma: no cover
    Github = None


class RepositoryAnalyzerService:
    def __init__(self) -> None:
        self.token = os.getenv("GITHUB_TOKEN")
        self.client = Github(self.token) if self.token and Github is not None else None

    def parse_url(self, url: str) -> Dict[str, Any]:
        pattern = r"https://github\.com/([^/]+)/([^/]+)(?:/.*)?"
        match = re.match(pattern, url.strip())
        if not match:
            raise ValueError("The provided URL is not a valid GitHub repository or profile URL.")

        owner, repo = match.groups()
        return {
            "owner": owner,
            "repo": repo,
            "is_github": True,
            "url": url,
        }

    def analyze_repository(self, url: str) -> Dict[str, Any]:
        parsed = self.parse_url(url)
        owner = parsed["owner"]
        repo_name = parsed["repo"]

        metadata: Dict[str, Any] = {
            "owner": owner,
            "repo": repo_name,
            "name": f"{owner}/{repo_name}",
            "description": "Repository metadata gathered from the GitHub URL.",
            "readme": "",
            "languages": ["Unknown"],
            "topics": [],
            "dependencies": [],
            "commit_history": [],
        }

        try:
            if self.client:
                repository = self.client.get_repo(f"{owner}/{repo_name}")
                metadata.update(
                    {
                        "description": repository.description or metadata["description"],
                        "topics": repository.get_topics(),
                        "languages": list(repository.get_languages().keys()),
                    }
                )
                readme = repository.get_readme().decoded_content.decode("utf-8", errors="ignore")
                metadata["readme"] = readme
                commits = repository.get_commits()[:5]
                metadata["commit_history"] = [commit.commit.message for commit in commits]
            else:
                api_url = f"https://api.github.com/repos/{owner}/{repo_name}"
                response = requests.get(api_url, timeout=10)
                if response.ok:
                    payload = response.json()
                    metadata.update(
                        {
                            "description": payload.get("description") or metadata["description"],
                            "topics": payload.get("topics", []),
                        }
                    )
                    readme_response = requests.get(
                        f"https://raw.githubusercontent.com/{owner}/{repo_name}/main/README.md",
                        timeout=10,
                    )
                    if readme_response.ok:
                        metadata["readme"] = readme_response.text
        except Exception:
            metadata["description"] = "Repository metadata could not be fetched from GitHub; using a local fallback summary."

        return metadata
