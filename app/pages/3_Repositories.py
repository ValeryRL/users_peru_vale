import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Repository Browser", page_icon="📁", layout="wide")
st.title("Repository Browser")

@st.cache_data(ttl=60)
def load_data():
    # Force reload
    _ = os.path.getmtime("data/processed/repositories.csv") if os.path.exists("data/processed/repositories.csv") else 0
    try:
        repos_df = pd.read_csv("data/processed/repositories.csv")
    except:
        repos_df = pd.DataFrame()
        
    try:
        classifications_df = pd.read_csv("data/processed/classifications.csv")
    except:
        classifications_df = pd.DataFrame()
        
    if not repos_df.empty and not classifications_df.empty:
        # Merge if id columns match properly. classifications has 'repo_id' while repos has 'id'
        if "id" in repos_df.columns and "repo_id" in classifications_df.columns:
            repos_df = repos_df.merge(
                classifications_df[["repo_id", "industry_name", "confidence"]], 
                left_on="id", right_on="repo_id", 
                how="left"
            )
            
    return repos_df

repos_df = load_data()

if repos_df.empty:
    st.warning("No repository data available. Please run the extraction scripts.")
    st.stop()

st.markdown("### Search and Filter Repositories")

col_search, col_filters_min = st.columns([2, 1])

with col_search:
    search_query = st.text_input("Search by repository name or description", "")
    
filtered_df = repos_df.copy()
if search_query:
    filtered_df = filtered_df[
        filtered_df["name"].str.contains(search_query, case=False, na=False) |
        filtered_df["description"].str.contains(search_query, case=False, na=False)
    ]

col1, col2, col3 = st.columns(3)

with col1:
    industries = []
    if "industry_name" in filtered_df.columns:
        industries = sorted(filtered_df["industry_name"].dropna().unique().tolist())
    industry_filter = st.multiselect("Industry", options=industries)
    if industry_filter:
        filtered_df = filtered_df[filtered_df["industry_name"].isin(industry_filter)]

with col2:
    languages = []
    if "language" in filtered_df.columns:
        languages = sorted(filtered_df["language"].dropna().unique().tolist())
    lang_filter = st.multiselect("Primary Language", options=languages)
    if lang_filter:
        filtered_df = filtered_df[filtered_df["language"].isin(lang_filter)]

with col3:
    max_stars_val = int(repos_df["stargazers_count"].max()) if not repos_df.empty else 1000
    min_stars = st.slider("Minimum Stars", 0, max_stars_val, 0)
    if min_stars > 0:
        filtered_df = filtered_df[filtered_df["stargazers_count"] >= min_stars]

st.markdown(f"**Found {len(filtered_df)} repositories**")

display_cols = [
    "name", "owner", "stargazers_count", "language", "industry_name", "description"
]
# Filter out missing columns
display_cols = [c for c in display_cols if c in filtered_df.columns]

st.dataframe(
    filtered_df[display_cols].sort_values(by="stargazers_count", ascending=False),
    use_container_width=True,
    hide_index=True
)

st.download_button(
    label="Download repositories data",
    data=filtered_df.to_csv(index=False).encode("utf-8"),
    file_name="repositories_filtered.csv",
    mime="text/csv",
)
