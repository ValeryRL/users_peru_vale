import streamlit as st
import pandas as pd

st.set_page_config(page_title="Developer Explorer", page_icon="👥", layout="wide")
st.title("Developer Explorer")

@st.cache_data
def load_data():
    try:
        users_df = pd.read_csv("data/metrics/user_metrics.csv")
        return users_df
    except:
        return pd.DataFrame()

users_df = load_data()

if users_df.empty:
    st.warning("No logic data available. Please run scripts/calculate_metrics.py first.")
    st.stop()

# Filters
st.markdown("### Filter Developers")
col1, col2, col3 = st.columns(3)

with col1:
    min_stars = st.slider("Minimum Total Stars Received", 0, int(users_df["total_stars_received"].max()) if not users_df.empty else 1000, 0)

with col2:
    languages = []
    if "primary_language_1" in users_df.columns:
        languages = users_df["primary_language_1"].dropna().unique().tolist()
    language_filter = st.multiselect("Primary Language", options=languages)

with col3:
    active_only = st.checkbox("Active developers only (Last 90 days)", value=False)
    
# Apply filters
filtered_df = users_df.copy()

if min_stars > 0:
    filtered_df = filtered_df[filtered_df["total_stars_received"] >= min_stars]

if language_filter:
    filtered_df = filtered_df[filtered_df["primary_language_1"].isin(language_filter)]

if active_only:
    # Handle potentially missing or differently typed boolean column
    if "is_active" in filtered_df.columns:
        # Convert strings to bool if needed
        is_active_mask = filtered_df["is_active"].astype(str).str.lower() == 'true'
        filtered_df = filtered_df[is_active_mask]

# Display results
st.markdown(f"**Showing {len(filtered_df)} developers**")

display_cols = [
    "login", "name", "total_repos", "total_stars_received", 
    "followers", "impact_score", "primary_language_1", "h_index"
]
# Filter out missing columns
display_cols = [c for c in display_cols if c in filtered_df.columns]

st.dataframe(
    filtered_df[display_cols].sort_values(by="impact_score", ascending=False),
    use_container_width=True,
    hide_index=True
)

st.download_button(
    label="Download filtered data as CSV",
    data=filtered_df.to_csv(index=False).encode("utf-8"),
    file_name="developers_filtered.csv",
    mime="text/csv",
)
