import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="customma",  # Title displayed in the browser tab
)

# Streamlit app setup
# st.title("customer segmentation::RFM analysis")
st.markdown('<h1 style="font-size:30px;">customer segmentation::RFM analysis</h1>', unsafe_allow_html=True)

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

    quantiles = rfm[['Recency','Frequency','MonetaryValue']].quantile(q=[0.25,0.5,0.75])
    # st.write("RFM dtypes:")
    # st.dataframe(rfm.dtypes)
    st.write("RFM quantiles:")
    st.dataframe(quantiles)

    # create the RFM segmentation table
    rfmSegmentation = rfm


    # Arguments (x = value, p = recency, monetary_value, frequency, k = quartiles dict)
    def RClass(x, p, d):
        if x <= d[p][0.25]:
            return 1
        elif x <= d[p][0.50]:
            return 2
        elif x <= d[p][0.75]:
            return 3
        else:
            return 4

    # Arguments (x = value, p = recency, monetary_value, frequency, k = quartiles dict)
    def FMClass(x, p, d):
        if x <= d[p][0.25]:
            return 4
        elif x <= d[p][0.50]:
            return 3
        elif x <= d[p][0.75]:
            return 2
        else:
            return 1


    rfmSegmentation['R_Quartile'] = rfmSegmentation['Recency'].apply(RClass, args=('Recency', quantiles,))
    rfmSegmentation['F_Quartile'] = rfmSegmentation['Frequency'].apply(FMClass, args=('Frequency', quantiles,))
    rfmSegmentation['M_Quartile'] = rfmSegmentation['MonetaryValue'].apply(FMClass,
                                                                            args=('MonetaryValue', quantiles,))

    rfmSegmentation['RFMClass'] = rfmSegmentation.R_Quartile.map(str) \
                                  + rfmSegmentation.F_Quartile.map(str) \
                                  + rfmSegmentation.M_Quartile.map(str)

    st.write("Segment per customer:")
    st.dataframe(rfmSegmentation)
