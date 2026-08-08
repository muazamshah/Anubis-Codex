from backend.services.github_service import RepositoryAnalyzerService


def test_parse_github_url():
    service = RepositoryAnalyzerService()
    payload = service.parse_url("https://github.com/openai/openai-cookbook")

    assert payload["owner"] == "openai"
    assert payload["repo"] == "openai-cookbook"
    assert payload["is_github"] is True
