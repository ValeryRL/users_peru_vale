import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Language Analytics", page_icon="💻", layout="wide")
st.title("Language Analytics")

@st.cache_data
def load_data():
    try:
        repos_df = pd.read_csv("data/processed/repositories.csv")
    except:
        repos_df = pd.DataFrame()
        
    try:
        classifications_df = pd.read_csv("data/processed/classifications.csv")
    except:
        classifications_df = pd.DataFrame()
        
    if not repos_df.empty and not classifications_df.empty:
        if "id" in repos_df.columns and "repo_id" in classifications_df.columns:
            repos_df = repos_df.merge(
                classifications_df[["repo_id", "industry_name"]], 
                left_on="id", right_on="repo_id", 
                how="left"
            )
            
    return repos_df

df = load_data()

if df.empty or "language" not in df.columns:
    st.warning("No language data available. Please run the extraction scripts.")
    st.stop()

col1, col2 = st.columns(2)

with col1:
    st.subheader("Programming Language Distribution")
    lang_counts = df["language"].dropna().value_counts().head(15).reset_index()
    lang_counts.columns = ["Language", "Count"]
    
    fig_lang = px.bar(
        lang_counts,
        x="Language",
        y="Count",
        title="Top 15 Primary Languages",
        color="Count",
        color_continuous_scale="Spectral"
    )
    st.plotly_chart(fig_lang, use_container_width=True)

with col2:
    st.subheader("Language Popularity by Stars")
    if "stargazers_count" in df.columns:
        df["stargazers_count"] = pd.to_numeric(df["stargazers_count"], errors="coerce").fillna(0)
        stars_by_lang = df.groupby("language")["stargazers_count"].sum().reset_index()
        stars_by_lang = stars_by_lang.sort_values("stargazers_count", ascending=False).head(15)
        
        fig_stars = px.bar(
            stars_by_lang,
            x="stargazers_count",
            y="language",
            orientation="h",
            title="Top 15 Languages by Total Stars",
            color="stargazers_count",
            color_continuous_scale="Viridis"
        )
        fig_stars.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_stars, use_container_width=True)

st.markdown("---")
st.subheader("Industry by Language Correlation")

if "industry_name" in df.columns and "language" in df.columns:
    st.markdown("This heatmap shows which programming languages are most commonly used in which industry sectors.")
    
    # Filter top languages and industries to make heatmap readable
    top_langs = df["language"].value_counts().head(10).index.tolist()
    top_inds = df["industry_name"].value_counts().head(10).index.tolist()
    
    heatmap_data = df[df["language"].isin(top_langs) & df["industry_name"].isin(top_inds)]
    
    if not heatmap_data.empty:
        pivot = pd.crosstab(heatmap_data["industry_name"], heatmap_data["language"])
        
        fig_heat = px.imshow(
            pivot, 
            text_auto=True,
            aspect="auto",
            title="Heatmap: Top 10 Industries vs Top 10 Languages",
            color_continuous_scale="YlGnBu"
        )
        st.plotly_chart(fig_heat, use_container_width=True)
    else:
        st.info("Not enough data to generate correlation heatmap.")
else:
    st.info("Industry classification data required for correlation heatmap.")
