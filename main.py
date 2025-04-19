import pandas as pd
import streamlit as st
import numpy as np
import os
import altair as alt
import tomllib


st.set_page_config(
    page_title="customa",  # Title displayed in the browser tab
    layout="wide"
)

# insert logo, source: https://www.svgrepo.com/
working_directory = os.getcwd()
relative_path = "customa2.svg"
full_path = os.path.join(working_directory, relative_path)

with open(full_path, "r") as f:
    svg_content = f.read()

# Display the SVG
st.image(svg_content, width=80)

# Streamlit app setup
# st.title("customer segmentation::RFM analysis")
st.markdown(
    "<h1 style='font-size:30px;'>"
    "<span style='color:#E67300;'>customa</span> :: customer segmentation via RFM analysis"
    "</h1>",
    unsafe_allow_html=True
)

st.markdown(
    '<div style="line-height:1.5; margin:0; padding:0;">employing marketing analytics to develop customer-behavior'
    ' profiles based on past consumer data<br>customa transforms transactional data'
    ' into consumer profiles and insights<br>try out the app with the example .csv file or upload '
    'your own file</div>',
    unsafe_allow_html=True
)

st.markdown("""required file column layout: `[customerID, orderDate, orderID, orderValue]`""")

with open("example_data.toml", "rb") as f:
    example_data_dict = tomllib.load(f)

example_data = pd.DataFrame(example_data_dict)

# Convert the DataFrame to a CSV string
example_csv = example_data.to_csv(index=False).encode('utf-8')

# Add a download button for the example CSV file
st.download_button(
    label="download example .csv file",
    data=example_csv,
    file_name="example.csv",
    mime="text/csv"
)

# File uploader
uploaded_file = st.file_uploader(
    label="upload your CSV file",
    type=["csv"],
    help="comma-separated values required, orderDate format: 'dd/mm/yyyy'",
    label_visibility="visible"
)

# Apply custom CSS to adjust the width
css = '''
<style>
[data-testid='stFileUploader'] {
    width: 520px; /* Adjust the width as needed */
}
</style>
'''
st.markdown(css, unsafe_allow_html=True)

if uploaded_file:
    # Load the data
    df = pd.read_csv(uploaded_file, sep=",")

    # Ensure proper data types
    df['orderDate'] = pd.to_datetime(df['orderDate'], dayfirst=True)
    # Reindex to start from 1
    df.index = np.arange(1, len(df) + 1)
    # Name the index
    df.index.name = '#'
    # Set column headers to center alignment
    # pd.set_option('display.colheader_justify', 'center')

    metadata_dict = {
        '# of rows': len(df),
        '# of unique customers': df['customerID'].nunique(),
        'time period': "[" + min(df['orderDate']).strftime("%d/%m/%Y") + ", " +
                       max(df['orderDate']).strftime("%d/%m/%Y") + "]"
    }

    # Create two columns
    col1, col2 = st.columns([2, 1])
    # Display uploaded data in the left column
    with col1:
        st.write("data:")
        st.dataframe(df, height=220)
    # Create a chart using Plotly and display it in the right column
    with col2:
        st.write("metadata:")
        st.json(metadata_dict)

    # calculate snapshot date (max date + 1 day)
    snapshot_date = df['orderDate'].max() + pd.Timedelta(days=1)

    # calculate RFM metrics
    rfm = df.groupby('customerID').agg({
        'orderDate': lambda x: (snapshot_date - x.max()).days,  # Recency
        'orderID': lambda x: len(x),  # Frequency
        'orderValue': lambda x: x.sum()  # Monetary Value
    }).reset_index()

    # reindex to start from 1
    rfm.index = np.arange(1, len(rfm) + 1)
    # Name the index
    rfm.index.name = '#'

    rfm.rename(columns={
        'orderDate': 'Recency',
        'orderID': 'Frequency',
        'orderValue': 'MonetaryValue'
    }, inplace=True)

    st.write("RFM metrics:")
    st.dataframe(rfm)

    quantiles = rfm[['Recency', 'Frequency', 'MonetaryValue']].quantile(q=[0.25, 0.5, 0.75])
    # st.write("RFM dtypes:")
    # st.dataframe(rfm.dtypes)
    st.write("RFM quantiles:")
    st.dataframe(quantiles, width=400)

    # create the RFM segmentation table
    rfmSegmentation = rfm


    # arguments (x = value, p = recency, k = quartiles dict)
    def RClass(x, p, d):
        if x <= d[p][0.25]:
            return 1
        elif x <= d[p][0.50]:
            return 2
        elif x <= d[p][0.75]:
            return 3
        else:
            return 4


    # arguments (x = value, p = monetary_value OR frequency, k = quartiles dict)
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

    # Define mapping logic for profiles
    def rfm_segment(rfm_code):
        # Extract R, F, M as integers
        r, f, m = map(int, list(rfm_code))

        # Define rules based on common RFM segmentation logic
        if r == 1 and f == 1 and m == 1:
            return 'champion'
        elif r == 1 and f <= 2 and m <= 2:
            return 'loyal_customer'
        elif r <= 2 and f <= 3 and m <= 3:
            return 'potential_loyalist'
        elif r == 3 and f == 3 and m == 3:
            return 'needs_attention'
        elif r == 4 and f == 4 and m == 4:
            return 'at_risk'
        elif r >= 3 and f >= 3:
            return 'about_to_sleep'
        elif r == 4:
            return 'hibernating'
        else:
            return 'others'

    # Add column B using map
    rfmSegmentation['profile'] = rfmSegmentation['RFMClass'].apply(rfm_segment)

    # Inject custom CSS to set the width of the multiselect widget
    st.markdown("""
        <style>
        div[data-testid="stMultiSelect"] {
            width: 400px !important;  /* Set your desired width */
        }
        </style>
    """, unsafe_allow_html=True)

    # create dropdown filter options
    class_options = ['all'] + list(rfmSegmentation['profile'].unique())
    # create dropdown filter (multi-valued)
    selected_class = st.multiselect(
        'select customer profile(s):',
        options=class_options,
        default=None
    )

    # filter logic (filtered dataframe based on selection)
    if 'all' in selected_class or not selected_class:
        filtered_data = rfmSegmentation
    else:
        filtered_data = rfmSegmentation[rfmSegmentation['profile'].isin(selected_class)]
        # filtered_data = rfmSegmentation[rfmSegmentation['RFMClass'] == selected_class]

    # create two columns
    col1, col2 = st.columns([3, 1])
    # display RFM class per customer in the left column
    with col1:
        st.write("customer profiles:")
        st.dataframe(filtered_data)
    # display a chart of unique customers per RFM class in the right column
    with col2:
        st.markdown("<p style='text-align: center;'># customers per profile</p>", unsafe_allow_html=True)
        # count of unique customers per class
        counts = rfmSegmentation['profile'].value_counts().sort_values(ascending=False)
        counts_df = counts.reset_index()
        counts_df.columns = ['profile', '# customers']

        # create the bar chart
        c = alt.Chart(counts_df).mark_bar().encode(
            y=alt.Y('profile', sort=None),
            x=alt.X('# customers',
                    axis=alt.Axis(
                        format='.0f',  # Format to show no decimal places
                        tickMinStep=1#,  # Ensure minimum step between ticks is 1
                        # values=[1, 2, 3]  # Explicitly set ticks to avoid duplicates
                    )
                    )
        )

        st.altair_chart(c, use_container_width=True)
