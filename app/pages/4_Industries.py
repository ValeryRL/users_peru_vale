import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Industry Analysis", page_icon="🏭", layout="wide")
st.title("Industry Analysis")

@st.cache_data
def load_data():
    try:
        classifications_df = pd.read_csv("data/processed/classifications.csv")
        repos_df = pd.read_csv("data/processed/repositories.csv")
        if not repos_df.empty and not classifications_df.empty:
            merged_df = repos_df.merge(
                classifications_df, 
                left_on="id", right_on="repo_id", 
                how="inner"
            )
            return merged_df
        return classifications_df
    except:
        return pd.DataFrame()

df = load_data()

if df.empty:
    st.warning("No industry classification data available. Please run scripts/classify_repos.py first.")
    st.stop()

col1, col2 = st.columns(2)

with col1:
    st.subheader("Industry Distribution (All Repos)")
    ind_counts = df["industry_name"].value_counts().reset_index()
    ind_counts.columns = ["Industry", "Count"]
    
    fig_pie = px.pie(
        ind_counts, 
        values="Count", 
        names="Industry",
        hole=0.4,
        title="Distribution of Repositories across Industries"
    )
    st.plotly_chart(fig_pie, use_container_width=True)

with col2:
    st.subheader("Industry by Total Stars")
    if "stargazers_count" in df.columns:
        df["stargazers_count"] = pd.to_numeric(df["stargazers_count"], errors="coerce").fillna(0)
        stars_by_ind = df.groupby("industry_name")["stargazers_count"].sum().reset_index()
        stars_by_ind = stars_by_ind.sort_values("stargazers_count", ascending=False).head(10)
        
        fig_bar = px.bar(
            stars_by_ind,
            x="stargazers_count",
            y="industry_name",
            orientation="h",
            title="Top 10 Industries by Stars",
            labels={"stargazers_count": "Total Stars", "industry_name": "Industry"},
            color="stargazers_count",
            color_continuous_scale="Blues"
        )
        fig_bar.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.info("Additional repository metrics not available for cross-industry ranking.")

st.markdown("---")
st.subheader("AI Classification Confidence")

if "confidence" in df.columns:
    conf_counts = df["confidence"].value_counts().reset_index()
    conf_counts.columns = ["Confidence Level", "Count"]
    
    fig_conf = px.bar(
        conf_counts,
        x="Confidence Level",
        y="Count",
        title="GPT-4 Classification Confidence Distribution",
        color="Confidence Level",
        color_discrete_map={
            "high": "green", "medium": "orange", "low": "red"
        }
    )
    st.plotly_chart(fig_conf, use_container_width=True)
    
    # Show some edge cases if low confidence exists
    low_conf = df[df["confidence"] == "low"]
    if not low_conf.empty:
        st.markdown("#### Samples with Low Confidence Classifications")
        st.dataframe(low_conf[["repo_name", "industry_name", "reasoning"]].head(10))
