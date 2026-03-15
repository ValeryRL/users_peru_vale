import base64
from src.extraction.github_client import GitHubClient
from loguru import logger

class RepoExtractor:
    def __init__(self, client: GitHubClient):
        self.client = client

    def search_repos_by_stars(self, location_users: list[str], min_stars: int = 1) -> list[dict]:
        """
        Search for top repositories from users in a location.
        """
        repos = []
        for username in location_users:
            try:
                user_repos = self.client.make_request(
                    f"users/{username}/repos",
                    params={"sort": "stars", "direction": "desc", "per_page": 100}
                )
                
                # Note: user_repos might be a dict if there's an error, 
                # but make_request raises for status, so it's a list if successful
                if isinstance(user_repos, list):
                    for repo in user_repos:
                        if repo.get("stargazers_count", 0) >= min_stars:
                            repos.append(repo)
            except Exception as e:
                logger.error(f"Error fetching repos for user {username}: {e}")

        # Sort all repos by stars and take top 1000
        repos.sort(key=lambda x: x.get("stargazers_count", 0), reverse=True)
        return repos[:1000]

    def get_repo_readme(self, owner: str, repo: str) -> str:
        """
        Get the README content of a repository.
        Returns empty string if not found.
        """
        try:
            result = self.client.make_request(
                f"repos/{owner}/{repo}/readme"
            )
            content = base64.b64decode(result["content"]).decode("utf-8")
            return content[:5000]  # Limit to 5000 chars for API costs
        except Exception:
            return ""

    def get_repo_languages(self, owner: str, repo: str) -> dict:
        """Get the language breakdown of a repository."""
        try:
            return self.client.make_request(f"repos/{owner}/{repo}/languages")
        except Exception as e:
            logger.error(f"Error fetching languages for {owner}/{repo}: {e}")
            return {}

    def get_repo_contributors(self, owner: str, repo: str) -> list[dict]:
        """Get the contributors of a repository."""
        try:
            return self.client.make_request(
                f"repos/{owner}/{repo}/contributors",
                params={"per_page": 100}
            )
        except Exception as e:
            logger.error(f"Error fetching contributors for {owner}/{repo}: {e}")
            return []
