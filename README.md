# GitHub Peru Analytics: Developer Ecosystem Dashboard

A data analytics platform that extracts, processes, and visualizes information about the Peruvian developer ecosystem using the GitHub API.

## Section 1: Project Title and Description
**GitHub Peru Analytics**

This project extracts data from over 1,000 GitHub repositories associated with developers in Peru. It leverages the GitHub REST API to gather user and repository metrics, processes the data to calculate custom insights (like h-index and impact score), and uses an AI classification agent powered by GPT-4 to categorize repositories into 21 distinct industry sectors based on the CIIU standard. The insights are then presented through an interactive 5-page Streamlit dashboard.

*(Antigravity Easter egg screenshot will be added here)*

## Section 2: Key Findings
*(To be populated after data collection and analysis)*
- Top 5 insights about Peru's developer ecosystem
- Most popular languages
- Industry distribution highlights

## Section 3: Data Collection
- **Users/Repos collected:** (To be updated)
- **Time period:** (To be updated)
- **Rate limiting approach:** Exponential backoff with `tenacity`, respecting GitHub's rate limits and pause windows automatically via `GitHubClient`.

## Section 4: Features
- **Overview Dashboard:** Key ecosystem statistics, trend charts, and top developers/repos.
- **Developer Explorer:** Searchable and filterable table of all developers.
- **Repository Browser:** Advanced filtering for all collected repositories.
- **Industry Analysis:** AI-powered distribution of repositories across 21 industries.
- **Language Analytics:** Programming language trends and correlations.

## Section 5: Installation
1. Clone the repository: `git clone <repository-url>`
2. Install dependencies: `pip install -r requirements.txt`
3. Copy `.env.example` to `.env` and add your `GITHUB_TOKEN` and `OPENAI_API_KEY`.

## Section 6: Usage
1. Run Data Extraction: `python scripts/extract_data.py`
2. Run Classification: `python scripts/classify_repos.py`
3. Calculate Metrics: `python scripts/calculate_metrics.py`
4. Start Dashboard: `streamlit run app/main.py`

## Section 7: Metrics Documentation

### User-Level Metrics
- `total_repos`: Count of owned public repositories for the user.
- `total_stars_received`: Sum of stargazers across all repositories.
- `total_forks_received`: Sum of forks across all repositories.
- `avg_stars_per_repo`: `total_stars_received / total_repos`.
- `account_age_days`: Days elapsed since the account creation date.
- `repos_per_year`: `total_repos / (account_age_days / 365)`.
- `followers`: Direct number of followers from the API.
- `following`: Number of followings from the API.
- `follower_ratio`: `followers / following`.
- `h_index`: The maximum value of `h` such that the given user has published `h` repositories that have each been starred at least `h` times.
- `impact_score`: Composite impact calculated as `stars + (forks * 2) + followers`.
- `primary_languages`: Top 3 programming languages across repositories.
- `language_diversity`: Count of unique programming languages used.
- `industries_served`: Count of unique industry sectors categorizing the user's repos.
- `has_readme_pct`: Percentage of repositories containing a README.
- `has_license_pct`: Percentage of repositories containing a license.
- `total_open_issues`: Sum of open issues across all repos.
- `days_since_last_push`: Days elapsed since the most recent `pushed_at` date across all repos.
- `is_active`: Boolean evaluated to `True` if `days_since_last_push` is less than 90 days.

### Ecosystem Metrics
- `total_developers`: Count of unique Peru-associated developers processed.
- `total_repositories`: Total number of repositories analyzed (usually top 1000).
- `total_stars`: Sum of stars across all repositories analyzed.
- `avg_repos_per_user`: Average number of repositories per developer in the dataset.
- `most_popular_languages`: Top 10 primary programming languages across the ecosystem.
- `industry_distribution`: Distribution of the 21 classification sectors.
- `active_developer_pct`: Percentage of users who have pushed code within the last 90 days.
- `avg_account_age_days`: Average age of the developers' accounts.

## Section 8: AI Agent Documentation

### Classification Agent Architecture
The architecture includes an autonomous ReAct AI agent (`ClassificationAgent`) integrated with OpenAI's `gpt-4o-mini` via Function Calling. The agent is responsible for receiving basic repository information and deciding how to proceed with the classification into the CIIU sectors.

### Tools Available
1. **`get_readme(owner, repo)`**: Allows the agent to dynamically fetch up to the first 5000 characters of the repository's README to gain deeper contextual understanding when the repository description is vague or missing.
2. **`get_languages(owner, repo)`**: Fetches the map of programming languages and their byte sizes to determine what kind of software it is (e.g. Jupyter Notebooks for Data Science).
3. **`classify_industry(repo_name, industry_code, confidence, reasoning)`**: The final tool called by the agent to persist its decision, assign a confidence level (high/medium/low), and provide a log reasoning for the classification.

### Example Agent Flow
1. Agent receives repository "Sistema-Ventas" with no description.
2. Agent realizes it lacks context and autonomously decides to call `get_readme("ValeryRL", "Sistema-Ventas")`.
3. The tool returns README indicating it's a point-of-sale app for a minimarket.
4. Agent reads the response and finally calls `classify_industry` with industry code `G` (Wholesale and retail trade) and "high" confidence, citing the retail usage mentioned in the README.

## Section 9: Limitations
1. **API Stagnation:** Data extraction heavily limits the search volume due to GitHub's REST API limitation (max 1000 search results per condition), potentially neglecting newer developers not highly positioned by followers.
2. **Geographical Ambiguity:** Extracting developers purely relies on user-typed string locations ("Peru", "Lima"). Developers who omit their location or type something unrelated are completely excluded from the ecosystem analysis (False negatives).
3. **LLM Hallucination/Bias:** Given the lack of extensive context for many empty repositories, the AI classifier might default heavily to generic sectors (like "Information and communication") or make assumptions based solely on repository names.

## Section 10: Author Information
- **Name:** PC
- **Course information:** Developer Ecosystem Assignment
- **Date:** 2026-03-14
