import streamlit as st
import pandas as pd

from dashboard import show_dashboard

st.set_page_config(
    page_title="AI-Powered Data Analytics Assistant",
    layout="wide"
)

st.title("AI-Powered Data Analytics Assistant")

st.write(
    "Upload your CSV dataset to explore visualizations "
    "and generate AI-powered business insights."
)

uploaded_file = st.file_uploader(
    "Upload your CSV file",
    type=["csv"]
)

if uploaded_file is not None:

    try:
        df = pd.read_csv(uploaded_file)

        st.success("Dataset uploaded successfully!")

        show_dashboard(
            df,
            key_prefix="uploaded_csv"
        )

    except Exception as e:
        st.error(f"Error processing dataset: {e}")

else:
    st.info("Please upload a CSV file to get started.")
