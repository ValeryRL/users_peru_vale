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
*(To be populated)*

## Section 8: AI Agent Documentation
*(To be populated)*

## Section 9: Limitations
*(To be populated)*

## Section 10: Author Information
- **Name:** PC
- **Course information:** Developer Ecosystem Assignment
- **Date:** 2026-03-14
