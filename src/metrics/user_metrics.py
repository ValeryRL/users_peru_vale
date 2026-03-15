from datetime import datetime, timedelta
from collections import Counter
import pandas as pd

class UserMetricsCalculator:
    def __init__(self):
        # We use a fixed date for "today" when evaluating to ensure tests/metrics are consistent
        # or just dynamic now()
        self.today = datetime.now()

    def _calculate_h_index(self, repos: list[dict]) -> int:
        """
        Calculate h-index based on repository stars.
        h-index = h if h repos have at least h stars each.
        """
        stars = sorted([r.get("stargazers_count", 0) for r in repos], reverse=True)
        h = 0
        for i, s in enumerate(stars):
            if s >= i + 1:
                h = i + 1
            else:
                break
        return h

    def calculate_all_metrics(
        self,
        user: dict,
        repos: list[dict],
        classifications: list[dict]
    ) -> dict:
        """
        Calculate all user-level metrics.
        """
        metrics = {"user_id": user.get("id"), "login": user.get("login"), "name": user.get("name")}

        # Check for empty state
        if not repos:
            repos = []

        # Ensure numeric values are integers, as CSV might load them as floats or strings
        for repo in repos:
            repo["stargazers_count"] = int(repo.get("stargazers_count", 0) or 0)
            repo["forks_count"] = int(repo.get("forks_count", 0) or 0)
            repo["open_issues_count"] = int(repo.get("open_issues_count", 0) or 0)
        
        # Activity Metrics
        metrics["total_repos"] = len(repos)
        metrics["total_stars_received"] = sum(r.get("stargazers_count", 0) for r in repos)
        metrics["total_forks_received"] = sum(r.get("forks_count", 0) for r in repos)
        
        metrics["avg_stars_per_repo"] = (
            metrics["total_stars_received"] / metrics["total_repos"]
            if metrics["total_repos"] > 0 else 0
        )
        
        try:
            created_at_val = str(user.get("created_at", self.today.isoformat()))
            created_at = datetime.fromisoformat(created_at_val.replace("Z", "+00:00")).replace(tzinfo=None)
            metrics["account_age_days"] = max(1, (self.today - created_at).days)
        except Exception:
            metrics["account_age_days"] = 1
            
        metrics["repos_per_year"] = (
            metrics["total_repos"] / (metrics["account_age_days"] / 365)
            if metrics["account_age_days"] > 0 else 0
        )
        
        # Influence Metrics
        metrics["followers"] = int(user.get("followers", 0) or 0)
        metrics["following"] = int(user.get("following", 0) or 0)
        metrics["follower_ratio"] = (
            metrics["followers"] / metrics["following"]
            if metrics["following"] > 0 else metrics["followers"]
        )
        
        metrics["h_index"] = self._calculate_h_index(repos)
        metrics["impact_score"] = (
            metrics["total_stars_received"] +
            (metrics["total_forks_received"] * 2) +
            metrics["followers"]
        )
        
        # Technical Metrics
        languages = []
        for r in repos:
            if isinstance(r.get("language"), str) and r.get("language"):
                languages.append(r.get("language"))
        
        lang_counts = Counter(languages)
        metrics["primary_languages"] = ", ".join([l for l, _ in lang_counts.most_common(3)])
        
        # Add primary language 1, 2, 3 as separate columns for easier filtering later in streamlit
        top_langs = lang_counts.most_common(3)
        metrics["primary_language_1"] = top_langs[0][0] if len(top_langs) > 0 else None
        
        metrics["language_diversity"] = len(set(languages))
        
        industry_codes = [c.get("industry_code") for c in classifications if c.get("industry_code")]
        metrics["industries_served"] = len(set(industry_codes))
        
        primary_industry = Counter(industry_codes).most_common(1)
        metrics["primary_industry"] = primary_industry[0][0] if primary_industry else None
        
        # Documentation quality
        repos_with_readme = sum(1 for r in repos if str(r.get("has_readme", "")).lower() == "true" or r.get("has_readme") == True)
        repos_with_license = sum(1 for r in repos if str(r.get("has_license", "")).lower() == "true" or r.get("has_license") == True)
        
        metrics["has_readme_pct"] = repos_with_readme / len(repos) if repos else 0
        metrics["has_license_pct"] = repos_with_license / len(repos) if repos else 0
        
        # Engagement Metrics
        metrics["total_open_issues"] = sum(r.get("open_issues_count", 0) for r in repos)
        
        if repos:
            valid_pushed_dates = []
            for r in repos:
                p_at = r.get("pushed_at")
                if p_at and isinstance(p_at, str):
                    try:
                        valid_pushed_dates.append(datetime.fromisoformat(p_at.replace("Z", "+00:00")).replace(tzinfo=None))
                    except ValueError:
                        pass
            
            if valid_pushed_dates:
                last_push = max(valid_pushed_dates)
                metrics["days_since_last_push"] = (self.today - last_push).days
                metrics["is_active"] = metrics["days_since_last_push"] < 90
            else:
                metrics["days_since_last_push"] = None
                metrics["is_active"] = False
        else:
            metrics["days_since_last_push"] = None
            metrics["is_active"] = False
            
        return metrics
