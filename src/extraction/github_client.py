import os
import requests
import time
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential
from loguru import logger

load_dotenv()

class GitHubClient:
    def __init__(self):
        self.token = os.getenv("GITHUB_TOKEN")
        if not self.token or self.token == "your_github_token_here":
            logger.warning("GITHUB_TOKEN not properly configured.")
            
        self.base_url = "https://api.github.com"
        self.headers = {
            "Accept": "application/vnd.github.v3+json"
        }
        
        if self.token:
            self.headers["Authorization"] = f"token {self.token}"

    def check_rate_limit(self) -> dict:
        """Check current rate limit status."""
        response = requests.get(
            f"{self.base_url}/rate_limit",
            headers=self.headers
        )
        return response.json()

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=60)
    )
    def make_request(self, endpoint: str, params: dict = None) -> dict:
        """Make a rate-limit-aware request to GitHub API."""
        response = requests.get(
            f"{self.base_url}/{endpoint}",
            headers=self.headers,
            params=params
        )
        
        # Check rate limit
        remaining = int(response.headers.get("X-RateLimit-Remaining", 0))
        if remaining < 10:
            reset_time = int(response.headers.get("X-RateLimit-Reset", 0))
            current_time = int(time.time())
            sleep_time = max(0, reset_time - current_time) + 5  # added buffer
            
            logger.warning(f"Rate limit approaching. Waiting {sleep_time} seconds until reset.")
            time.sleep(sleep_time)
            
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            if response.status_code == 403 and "API rate limit exceeded" in response.text:
                reset_time = int(response.headers.get("X-RateLimit-Reset", int(time.time()) + 60))
                sleep_time = max(0, reset_time - int(time.time())) + 5
                logger.warning(f"Rate limit exceeded. Forced wait for {sleep_time} seconds.")
                time.sleep(sleep_time)
                # Retry manually instead of depending only on tenacity to avoid losing the attempt
                return self.make_request(endpoint, params)
            raise e
            
        return response.json()
