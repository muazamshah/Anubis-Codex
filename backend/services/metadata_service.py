import os
from typing import Any, Dict, List


class MetadataService:
    def extract_metadata(self, repo_path: str, github_metadata: Dict[str, Any]) -> Dict[str, Any]:
        readme_content = self._extract_readme(repo_path)
        dependencies = self._extract_dependencies(repo_path)
        commit_history = github_metadata.get("commit_history", [])

        return {
            "name": github_metadata.get("name", ""),
            "owner": github_metadata.get("owner", ""),
            "description": github_metadata.get("description", ""),
            "readme": readme_content,
            "languages": github_metadata.get("languages", []),
            "topics": github_metadata.get("topics", []),
            "dependencies": dependencies,
            "commit_history": commit_history,
            "url": github_metadata.get("url", ""),
        }

    def _extract_readme(self, repo_path: str) -> str:
        readme_files = ["README.md", "README.rst", "README.txt", "README"]
        for readme_file in readme_files:
            readme_path = os.path.join(repo_path, readme_file)
            if os.path.exists(readme_path):
                try:
                    with open(readme_path, "r", encoding="utf-8", errors="ignore") as f:
                        return f.read()
                except Exception:
                    continue
        return ""

    def _extract_dependencies(self, repo_path: str) -> List[str]:
        dependencies: List[str] = []

        # Python - requirements.txt
        requirements_path = os.path.join(repo_path, "requirements.txt")
        if os.path.exists(requirements_path):
            try:
                with open(requirements_path, "r", encoding="utf-8", errors="ignore") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#"):
                            dependencies.append(line.split("==")[0].split(">=")[0].split("<=")[0])
            except Exception:
                pass

        # Node.js - package.json
        package_json_path = os.path.join(repo_path, "package.json")
        if os.path.exists(package_json_path):
            try:
                import json
                with open(package_json_path, "r", encoding="utf-8", errors="ignore") as f:
                    data = json.load(f)
                    deps = data.get("dependencies", {})
                    dev_deps = data.get("devDependencies", {})
                    dependencies.extend(list(deps.keys()) + list(dev_deps.keys()))
            except Exception:
                pass

        # Java - pom.xml
        pom_xml_path = os.path.join(repo_path, "pom.xml")
        if os.path.exists(pom_xml_path):
            try:
                with open(pom_xml_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                    # Simple extraction - look for <artifactId> tags
                    import re
                    artifacts = re.findall(r"<artifactId>(.*?)</artifactId>", content)
                    dependencies.extend(artifacts[:20])
            except Exception:
                pass

        return list(set(dependencies))