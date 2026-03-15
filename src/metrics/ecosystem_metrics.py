import pandas as pd
from collections import Counter

class EcosystemMetricsCalculator:
    def calculate_ecosystem_metrics(self, users_df: pd.DataFrame, repos_df: pd.DataFrame, classifications_df: pd.DataFrame, user_metrics_df: pd.DataFrame) -> dict:
        """Calculate these metrics for the entire Peru ecosystem."""
        
        total_developers = len(users_df) if not users_df.empty else 0
        total_repositories = len(repos_df) if not repos_df.empty else 0
        
        total_stars = 0
        if not repos_df.empty and "stargazers_count" in repos_df.columns:
            # Ensure numeric
            total_stars = pd.to_numeric(repos_df["stargazers_count"], errors="coerce").fillna(0).sum()
            
        avg_repos_per_user = total_repositories / total_developers if total_developers > 0 else 0
        
        most_popular_languages = {}
        if not repos_df.empty and "language" in repos_df.columns:
            langs = repos_df["language"].dropna().tolist()
            most_popular_languages = dict(Counter(langs).most_common(10))
            
        industry_distribution = {}
        if not classifications_df.empty and "industry_name" in classifications_df.columns:
            ind_counts = classifications_df["industry_name"].value_counts()
            industry_distribution = ind_counts.to_dict()
            
        active_developer_pct = 0
        if not user_metrics_df.empty and "is_active" in user_metrics_df.columns:
            # Boolean mapping
            active_count = user_metrics_df["is_active"].astype(bool).sum()
            active_developer_pct = (active_count / len(user_metrics_df)) * 100
            
        avg_account_age = 0
        if not user_metrics_df.empty and "account_age_days" in user_metrics_df.columns:
            avg_account_age = pd.to_numeric(user_metrics_df["account_age_days"], errors="coerce").mean()
            
        return {
            "total_developers": int(total_developers),
            "total_repositories": int(total_repositories),
            "total_stars": int(total_stars),
            "avg_repos_per_user": float(avg_repos_per_user),
            "most_popular_languages": most_popular_languages,
            "industry_distribution": industry_distribution,
            "active_developer_pct": float(active_developer_pct),
            "avg_account_age_days": float(avg_account_age)
        }
