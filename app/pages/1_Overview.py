import streamlit as st
import pandas as pd
import plotly.express as px
import json
import os

st.set_page_config(page_title="Overview - GitHub Peru", page_icon="🇵🇪", layout="wide")
st.title("Peru Developer Ecosystem Overview")

@st.cache_data
def load_data():
    try:
        users_df = pd.read_csv("data/metrics/user_metrics.csv")
    except:
        users_df = pd.DataFrame()
        
    try:
        with open("data/metrics/ecosystem_metrics.json", "r") as f:
            ecosystem_metrics = json.load(f)
    except:
        ecosystem_metrics = {}
        
    try:
        repos_df = pd.read_csv("data/processed/repositories.csv")
        # Ensure 'stargazers_count' is numeric
        if 'stargazers_count' in repos_df.columns:
            repos_df['stargazers_count'] = pd.to_numeric(repos_df['stargazers_count'], errors='coerce').fillna(0)
    except:
        repos_df = pd.DataFrame()
        
    try:
        classifications_df = pd.read_csv("data/processed/classifications.csv")
    except:
        classifications_df = pd.DataFrame()
        
    return users_df, repos_df, classifications_df, ecosystem_metrics

users_df, repos_df, classifications_df, ecosystem_metrics = load_data()

if not ecosystem_metrics:
    st.warning("No data found. Please run scripts/calculate_metrics.py first.")
    st.stop()

# Key metrics
st.markdown("### Ecosystem Highlights")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Developers", f"{ecosystem_metrics.get('total_developers', 0):,}")
with col2:
    st.metric("Total Repositories", f"{ecosystem_metrics.get('total_repositories', 0):,}")
with col3:
    st.metric("Total Stars", f"{ecosystem_metrics.get('total_stars', 0):,}")
with col4:
    active_pct = ecosystem_metrics.get("active_developer_pct", 0)
    st.metric("Active Developers (90 days)", f"{active_pct:.1f}%")

st.markdown("---")

col_charts1, col_charts2 = st.columns(2)

with col_charts1:
    st.subheader("Top 10 Developers by Impact Score")
    if not users_df.empty and "impact_score" in users_df.columns:
        top_devs = users_df.nlargest(10, "impact_score")[["login", "impact_score"]].dropna()
        if not top_devs.empty:
            fig_devs = px.bar(
                top_devs, 
                x="impact_score", 
                y="login", 
                orientation='h',
                title="Top Developers",
                color="impact_score",
                color_continuous_scale="Viridis"
            )
            fig_devs.update_layout(yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig_devs, use_container_width=True)
        else:
            st.info("Not enough data to show top developers.")
    else:
        st.info("Metrics not available yet.")

with col_charts2:
    st.subheader("Top 10 Repositories by Stars")
    if not repos_df.empty and "stargazers_count" in repos_df.columns:
        top_repos = repos_df.nlargest(10, "stargazers_count")[["name", "stargazers_count"]].dropna()
        if not top_repos.empty:
            fig_repos = px.bar(
                top_repos, 
                x="stargazers_count", 
                y="name", 
                orientation='h',
                title="Top Repositories",
                color="stargazers_count",
                color_continuous_scale="Plasma"
            )
            fig_repos.update_layout(yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig_repos, use_container_width=True)
        else:
            st.info("Not enough data to show top repositories.")
    else:
        st.info("Repositories data not available.")

st.markdown("---")

col_charts3, col_charts4 = st.columns(2)

with col_charts3:
    st.subheader("Activity Timeline (Account Creations)")
    try:
        raw_users_df = pd.read_csv("data/processed/users.csv")
        if "created_at" in raw_users_df.columns:
            raw_users_df["created_year"] = pd.to_datetime(raw_users_df["created_at"]).dt.year
            yearly_counts = raw_users_df["created_year"].value_counts().reset_index()
            yearly_counts.columns = ["Year", "New Developers"]
            yearly_counts = yearly_counts.sort_values("Year")
            
            fig_timeline = px.line(
                yearly_counts, 
                x="Year", 
                y="New Developers", 
                title="Developer Onboarding Over Time",
                markers=True
            )
            st.plotly_chart(fig_timeline, use_container_width=True)
    except:
        st.info("Could not load account creation timeline.")

with col_charts4:
    st.subheader("Stars vs Forks for Top 100 Repos")
    if not repos_df.empty and "stargazers_count" in repos_df.columns and "forks_count" in repos_df.columns:
        scatter_data = repos_df.nlargest(100, "stargazers_count").dropna(subset=["stargazers_count", "forks_count"])
        if not scatter_data.empty:
            fig_scatter = px.scatter(
                scatter_data, 
                x="forks_count", 
                y="stargazers_count", 
                hover_data=["name", "owner"],
                title="Correlation between Stars and Forks",
                labels={"forks_count": "Forks", "stargazers_count": "Stars"},
                color="stargazers_count",
                color_continuous_scale="Turbo"
            )
            st.plotly_chart(fig_scatter, use_container_width=True)
