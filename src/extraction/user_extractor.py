from src.extraction.github_client import GitHubClient
from loguru import logger

class UserExtractor:
    def __init__(self, client: GitHubClient):
        self.client = client

    def search_users_by_location(self, location: str, max_users: int = 1000) -> list[dict]:
        """
        Search for users by location.
        """
        users = []
        page = 1
        per_page = 100  # Max allowed by GitHub

        logger.info(f"Searching for top {max_users} users in location: {location}")
        
        while len(users) < max_users:
            try:
                result = self.client.make_request(
                    "search/users",
                    params={
                        "q": f"location:{location}",
                        "per_page": per_page,
                        "page": page,
                        "sort": "followers",  # Get most influential first
                        "order": "desc"
                    }
                )
                
                if not result.get("items"):
                    break
                    
                items = result["items"]
                users.extend(items)
                
                logger.debug(f"Fetched {len(items)} users from page {page}. Total: {len(users)}")
                page += 1
                
                # GitHub search API limits to 1000 results
                if page * per_page > 1000:
                    break
                    
            except Exception as e:
                logger.error(f"Error fetching users on page {page}: {e}")
                break

        return users[:max_users]

    def get_user_details(self, username: str) -> dict:
        """Get detailed information for a specific user."""
        try:
            return self.client.make_request(f"users/{username}")
        except Exception as e:
            logger.error(f"Error fetching details for user {username}: {e}")
            return {}

    def get_user_repos(self, username: str) -> list[dict]:
        """Get all repositories for a user."""
        repos = []
        page = 1
        
        while True:
            try:
                result = self.client.make_request(
                    f"users/{username}/repos",
                    params={
                        "per_page": 100,
                        "page": page,
                        "type": "owner"  # Only owned repos, not forks
                    }
                )
                
                if not result:
                    break
                    
                repos.extend(result)
                page += 1
            except Exception as e:
                logger.error(f"Error fetching repos for user {username} on page {page}: {e}")
                break
                
        return repos
