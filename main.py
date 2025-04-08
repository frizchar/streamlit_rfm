import pandas as pd
import streamlit as st
from datetime import datetime

# Streamlit app setup
st.title("RFM Analysis")

# File uploader
uploaded_file = st.file_uploader(label="Upload your CSV file", type=["csv"])

if uploaded_file:
    # Load the data
    df = pd.read_csv(uploaded_file, sep=",")

    # Ensure proper data types
    df['orderDate'] = pd.to_datetime(df['orderDate'], dayfirst=True)

    st.write("Uploaded Data:")
    st.write(df.head())
