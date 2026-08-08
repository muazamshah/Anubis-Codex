from typing import Any, Dict, List


class RepositoryModel:
    """Repository data model for Phase 1."""
    
    @staticmethod
    def create_repository(url: str, owner: str, name: str) -> Dict[str, Any]:
        return {
            "url": url,
            "owner": owner,
            "name": name,
            "full_name": f"{owner}/{name}",
        }
    
    @staticmethod
    def create_metadata(
        repository: Dict[str, Any],
        files: List[Dict[str, Any]],
        languages: List[str],
        readme: str,
        dependencies: List[str],
        commit_history: List[str],
    ) -> Dict[str, Any]:
        return {
            "repository": repository,
            "files": files,
            "file_count": len(files),
            "languages": languages,
            "readme": readme,
            "dependencies": dependencies,
            "commit_history": commit_history,
        }