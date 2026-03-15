import os
import sys
import json
import pandas as pd
from loguru import logger
from tqdm import tqdm

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.metrics.user_metrics import UserMetricsCalculator
from src.metrics.ecosystem_metrics import EcosystemMetricsCalculator

def calculate_metrics():
    logger.info("Loading processed data...")
    users_path = "data/processed/users.csv"
    repos_path = "data/processed/repositories.csv"
    classifications_path = "data/processed/classifications.csv"
    
    if not os.path.exists(repos_path) or not os.path.exists(users_path):
        logger.error("Data files not found. Please run extract_data.py first.")
        return
        
    users_df = pd.read_csv(users_path)
    repos_df = pd.read_csv(repos_path)
    
    # Classifications might not exist if classify_repos.py hasn't been run or failed
    if os.path.exists(classifications_path):
        classifications_df = pd.read_csv(classifications_path)
    else:
        logger.warning(f"{classifications_path} not found. Industry metrics will be empty.")
        classifications_df = pd.DataFrame(columns=["repo_id", "repo_name", "industry_code", "industry_name"])

    # Convert to orient records for easy dictionary processing
    users = users_df.fillna("").to_dict(orient="records")
    repos = repos_df.fillna("").to_dict(orient="records")
    classifications = classifications_df.fillna("").to_dict(orient="records")
    
    # Group repos and classifications by user
    repos_by_user = {}
    for r in repos:
        owner = r.get("owner")
        if owner not in repos_by_user:
            repos_by_user[owner] = []
        repos_by_user[owner].append(r)
        
    classifs_by_repo = {str(c.get("repo_id")): c for c in classifications if c.get("repo_id")}
    
    logger.info("Calculating user metrics...")
    user_calc = UserMetricsCalculator()
    user_metrics_results = []
    
    for user in tqdm(users, desc="User Metrics"):
        login = user.get("login")
        user_repos = repos_by_user.get(login, [])
        
        # Get classifications for this user's repos
        user_classifs = []
        for ur in user_repos:
            repo_id = str(ur.get("id"))
            if repo_id in classifs_by_repo:
                user_classifs.append(classifs_by_repo[repo_id])
                
        metrics = user_calc.calculate_all_metrics(user, user_repos, user_classifs)
        user_metrics_results.append(metrics)
        
    os.makedirs("data/metrics", exist_ok=True)
    
    # Save user metrics
    logger.info("Saving user metrics to CSV...")
    user_metrics_df = pd.DataFrame(user_metrics_results)
    user_metrics_df.to_csv("data/metrics/user_metrics.csv", index=False)
    
    # Calculate ecosystem metrics
    logger.info("Calculating ecosystem metrics...")
    eco_calc = EcosystemMetricsCalculator()
    ecosystem_results = eco_calc.calculate_ecosystem_metrics(users_df, repos_df, classifications_df, user_metrics_df)
    
    with open("data/metrics/ecosystem_metrics.json", "w", encoding="utf-8") as f:
        json.dump(ecosystem_results, f, indent=2)
        
    logger.info("Metrics calculation complete!")

if __name__ == "__main__":
    calculate_metrics()
