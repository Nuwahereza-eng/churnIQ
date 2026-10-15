"""Telco Churn Insight: Streamlit entry point.

Run with:  streamlit run app.py
"""

import streamlit as st

pages = [
    st.Page("app_pages/0_Home.py", title="Home", icon="🏠", default=True),
    st.Page("app_pages/1_Data_Exploration.py", title="Data Exploration", icon="🔎"),
    st.Page("app_pages/2_Predict_Churn.py", title="Predict Churn", icon="🧮"),
    st.Page("app_pages/3_Batch_Prediction.py", title="Batch Prediction", icon="📄"),
    st.Page("app_pages/4_Model_Performance.py", title="Model Performance", icon="📊"),
    st.Page("app_pages/5_Insights.py", title="Insights", icon="💡"),
]

st.navigation(pages).run()
