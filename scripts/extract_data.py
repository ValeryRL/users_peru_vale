import os
import sys
import json
import pandas as pd
from loguru import logger
from tqdm import tqdm

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.extraction.github_client import GitHubClient
from src.extraction.user_extractor import UserExtractor
from src.extraction.repo_extractor import RepoExtractor

def ensure_directories():
    os.makedirs("data/raw/users", exist_ok=True)
    os.makedirs("data/raw/repos", exist_ok=True)
    os.makedirs("data/processed", exist_ok=True)

def extract_data():
    ensure_directories()
    
    client = GitHubClient()
    user_extractor = UserExtractor(client)
    repo_extractor = RepoExtractor(client)
    
    locations = ["Peru", "Lima", "Arequipa", "Cusco", "Trujillo"]
    
    all_users = []
    seen_users = set()
    
    logger.info("Starting user discovery by location...")
    for loc in locations:
        users = user_extractor.search_users_by_location(loc, max_users=400)
        for user in users:
            login = user.get("login")
            if login and login not in seen_users:
                seen_users.add(login)
                all_users.append(user)
                
    logger.info(f"Discovered {len(all_users)} unique users.")
    
    # We need 1000 repos total. Let's get the repos for our users.
    # To optimize API calls, we'll fetch full user details and their repos only for top-tier users 
    # until we hit a good pool of repositories.
    
    user_logins = [u["login"] for u in all_users]
    
    logger.info("Extracting repositories (sorted by stars)...")
    top_repos = repo_extractor.search_repos_by_stars(user_logins, min_stars=0)
    logger.info(f"Found {len(top_repos)} repositories matching criteria.")
    
    # Save raw repos
    with open("data/raw/repos/top_repos.json", "w", encoding="utf-8") as f:
        json.dump(top_repos, f, indent=2)
        
    # We need full data for the owners of these top repos
    repo_owners = set(repo["owner"]["login"] for repo in top_repos)
    logger.info(f"Extracting detailed profiles for {len(repo_owners)} repository owners...")
    
    detailed_users = []
    for owner in tqdm(repo_owners, desc="User details"):
        details = user_extractor.get_user_details(owner)
        if details:
            detailed_users.append(details)
            
    with open("data/raw/users/detailed_users.json", "w", encoding="utf-8") as f:
        json.dump(detailed_users, f, indent=2)
        
    # Get extra info for repositories: README and languages
    logger.info("Extracting README and languages for all repositories...")
    enriched_repos = []
    for repo in tqdm(top_repos, desc="Repo details"):
        owner = repo["owner"]["login"]
        repo_name = repo["name"]
        
        # Additional data calls
        readme = repo_extractor.get_repo_readme(owner, repo_name)
        languages_dict = repo_extractor.get_repo_languages(owner, repo_name)
        
        # We only care about the primary language for easy mapping, but let's keep the dict
        primary_language = repo.get("language")
        if not primary_language and languages_dict:
            # Get the language with max bytes
            primary_language = max(languages_dict.items(), key=lambda x: x[1])[0]
            
        repo_data = {
            "id": repo["id"],
            "owner": owner,
            "name": repo_name,
            "full_name": repo["full_name"],
            "description": repo.get("description", ""),
            "topics": repo.get("topics", []),
            "language": primary_language,
            "languages": list(languages_dict.keys()),
            "stargazers_count": repo.get("stargazers_count", 0),
            "forks_count": repo.get("forks_count", 0),
            "watchers_count": repo.get("watchers_count", 0),
            "open_issues_count": repo.get("open_issues_count", 0),
            "created_at": repo.get("created_at", ""),
            "updated_at": repo.get("updated_at", ""),
            "pushed_at": repo.get("pushed_at", ""),
            "license": repo.get("license", {}).get("key") if repo.get("license") else None,
            "has_license": bool(repo.get("license")),
            "readme": readme,
            "has_readme": bool(readme.strip())
        }
        enriched_repos.append(repo_data)
        
    # Save processed users to CSV
    logger.info("Saving to CSV...")
    users_df_data = []
    for u in detailed_users:
        users_df_data.append({
            "id": u.get("id"),
            "login": u.get("login"),
            "name": u.get("name"),
            "location": u.get("location"),
            "bio": u.get("bio"),
            "company": u.get("company"),
            "blog": u.get("blog"),
            "email": u.get("email"),
            "followers": u.get("followers", 0),
            "following": u.get("following", 0),
            "public_repos": u.get("public_repos", 0),
            "created_at": u.get("created_at"),
            "updated_at": u.get("updated_at")
        })
        
    pd.DataFrame(users_df_data).to_csv("data/processed/users.csv", index=False)
    
    # Save enriched repos to CSV
    repos_df = pd.DataFrame(enriched_repos)
    # Convert lists to strings for CSV serialization natively
    repos_df["topics"] = repos_df["topics"].apply(lambda x: ",".join(x) if isinstance(x, list) else "")
    repos_df["languages"] = repos_df["languages"].apply(lambda x: ",".join(x) if isinstance(x, list) else "")
    repos_df.to_csv("data/processed/repositories.csv", index=False)
    
    logger.info("Data extraction complete! You can find the raw and processed data in the 'data' directory.")

if __name__ == "__main__":
    extract_data()
