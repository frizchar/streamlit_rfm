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

    # Calculate snapshot date (max date + 1 day)
    snapshot_date = df['orderDate'].max() + pd.Timedelta(days=1)

    # Calculate RFM metrics
    rfm = df.groupby('customerID').agg({
        'orderDate': lambda x: (snapshot_date - x.max()).days,  # Recency
        'orderID': lambda x: len(x),  # Frequency
        'totalAmount': lambda x: x.sum()  # Monetary Value
    }).reset_index()

    rfm.rename(columns={
        'orderDate': 'Recency',
        'orderID': 'Frequency',
        'totalAmount': 'MonetaryValue'
    }, inplace=True)

    st.write("RFM Metrics:")
    st.dataframe(rfm)
