import streamlit as st

st.set_page_config(
    page_title="GitHub Peru Analytics",
    page_icon="🇵🇪",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("GitHub Peru Analytics: Developer Ecosystem Dashboard")

st.markdown("""
### Welcome to the GitHub Peru Analytics Dashboard!
Navigate through the pages on the left to explore different aspects of the Peruvian developer ecosystem:

- **1 Overview:** High-level metrics, trends, and top items.
- **2 Developers:** Detailed, searchable table of developers in the ecosystem.
- **3 Repositories:** Filter and search through all 1000+ collected repositories.
- **4 Industries:** AI-driven classification of repositories into 21 global industries.
- **5 Languages:** Programming language trends, distribution, and cross-pollination.

Use the sidebar to select a page!
""")

st.info("Ensure you have run the extraction scripts (`extract_data.py`, `classify_repos.py`, and `calculate_metrics.py`) so there is data available in the `data/` folder before proceeding to the specific pages.")
