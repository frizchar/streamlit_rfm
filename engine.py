import pandas as pd
import streamlit as st
import numpy as np
import altair as alt


def run_app(data: pd.DataFrame) -> None:
    # section title with line separator
    st.markdown(
        """
        <h2 style='
            text-align: center; 
            font-weight: bold; 
            margin-bottom: 1px;  /* reduce space below title */
            margin-top: 0;       /* remove space above title */
        '>
            data
        </h2>
        """,
        unsafe_allow_html=True
    )
    st.markdown(
        """
        <hr style='
            border: 3px solid #bbb; 
            width: 100%; 
            margin-top: 0;        /* remove space above line */
            margin-bottom: 16px;  /* optional space below line */
        '>
        """,
        unsafe_allow_html=True
    )

    # load the data in pandas dataframe format
    df = data

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

    # section title with line separator
    st.markdown(
        """
        <h2 style='
            text-align: center; 
            font-weight: bold; 
            margin-bottom: 1px;  /* reduce space below title */
            margin-top: 0;       /* remove space above title */
        '>
            RFM analysis
        </h2>
        """,
        unsafe_allow_html=True
    )
    st.markdown(
        """
        <hr style='
            border: 3px solid #bbb; 
            width: 100%; 
            margin-top: 0;        /* remove space above line */
            margin-bottom: 16px;  /* optional space below line */
        '>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        'RFM analysis is a customer segmentation technique that helps businesses identify and rank their '
        'most valuable customers by examining three key behavioral metrics: Recency, Frequency, and Monetary '
        'value. Recency (R) measures how recently a customer made their last purchase, with more recent '
        'activity indicating higher engagement. Frequency (F) tracks how often a customer makes purchases '
        'within a specific period, highlighting loyal and repeat buyers. Monetary value (M) assesses the '
        'total amount a customer has spent, identifying those who contribute most to revenue. Each customer '
        'receives a score from 1 to 4 for each metric, derived from historical transaction '
        'data-recent purchases and higher spend or frequency yield higher scores. The combined RFM '
        'scores allow businesses to segment customers for targeted marketing and retention strategies.'
    )

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

    # Section separator with title
    st.markdown(
        """
        <h2 style='
            text-align: center; 
            font-weight: bold; 
            margin-bottom: 1px;  /* reduce space below title */
            margin-top: 0;       /* remove space above title */
        '>
            profile analysis
        </h2>
        """,
        unsafe_allow_html=True
    )
    st.markdown(
        """
        <hr style='
            border: 3px solid #bbb; 
            width: 100%; 
            margin-top: 0;        /* remove space above line */
            margin-bottom: 16px;  /* optional space below line */
        '>
        """,
        unsafe_allow_html=True
    )

    # Inject custom CSS to set the width of the multiselect widget
    st.markdown("""
        <style>
        div[data-testid="stMultiSelect"] {
            width: 400px !important;  /* Set your desired width */
        }
        </style>
    """, unsafe_allow_html=True)
    """
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
    """
    # create two columns
    col1, col2 = st.columns([3, 1])
    # display RFM class per customer in the left column
    with col1:
        st.write("customer profiles:")
        st.dataframe(rfmSegmentation)
    # display a chart of unique customers per RFM class in the right column
    with col2:
        st.markdown("<p style='text-align: center;'># of customers per profile</p>", unsafe_allow_html=True)
        # count of unique customers per class
        counts = rfmSegmentation['profile'].value_counts().sort_values(ascending=False)
        counts_df = counts.reset_index()
        counts_df.columns = ['profile', '# customers']

        # Calculate the angle for the pie chart
        # counts_df['angle'] = counts_df['# customers'] / counts_df['# customers'].sum() * 2 * 3.14159

        # Pie chart without legend
        pie = alt.Chart(counts_df).mark_arc(innerRadius=50).encode(
            theta=alt.Theta(field="# customers", type="quantitative"),
            color=alt.Color(field="profile", type="nominal", legend=None),  # Hide legend here
            tooltip=['profile', '# customers']
        ).properties(
            width=150,
            height=150
        )

        # Create a legend using a dummy chart with legend only
        legend_chart = alt.Chart(counts_df).mark_point().encode(
            y=alt.Y('profile:N', axis=alt.Axis(title=None, labels=True, ticks=False)),
            color=alt.Color('profile:N', legend=alt.Legend(orient='right', title='Profile'))
        ).properties(
            width=100,
            height=100
        )

        # Concatenate pie and legend horizontally
        final_chart = alt.hconcat(
            pie,
            legend_chart
        ).configure_view(
            strokeWidth=0
        )

        st.altair_chart(final_chart, use_container_width=False)

        st.markdown("<p style='text-align: center;'>mean monetary value - heatmap</p>", unsafe_allow_html=True)
        # Pivot the data to get the mean monetary value for each R-F combination
        rfm_pivot = rfmSegmentation.groupby(['R_Quartile', 'F_Quartile'])['MonetaryValue'].mean().round(0).reset_index()

        # Create the Altair heatmap
        heatmap = alt.Chart(rfm_pivot).mark_rect().encode(
            x=alt.X('F_Quartile:O', title='Frequency score'),
            y=alt.Y('R_Quartile:O', title='Recency score'),
            color=alt.Color('MonetaryValue:Q', title='mean mon.value', scale=alt.Scale(scheme='blues')),
            tooltip=['R_Quartile', 'F_Quartile', 'MonetaryValue']
        ).properties(
            width=900,
            height=180  #, title='RFM Heatmap: Mean Monetary Value by Recency and Frequency'
        )

        # Display in Streamlit
        st.altair_chart(heatmap, use_container_width=True)

    # create two columns
    col1, col2, col3 = st.columns([1, 1, 1])
    # display RFM class per customer in the left column
    with col1:
        st.markdown("<p style='text-align: center;'>average recency per profile</p>", unsafe_allow_html=True)
        # Calculate average recency per segment
        avg_r = rfmSegmentation.groupby('profile')['Recency'].mean().round(0).sort_values(ascending=True)
        avg_r_df = avg_r.reset_index()
        avg_r_df.columns = ['profile', 'avg_r']

        # create the bar chart
        c2r = alt.Chart(avg_r_df).mark_bar().encode(
            y=alt.Y('profile', sort=None),
            x=alt.X('avg_r',
                    axis=alt.Axis(title=None)
                    ),
            color=alt.Color(
                'avg_r',
                scale=alt.Scale(scheme='reds', reverse=True),  # Choose a color scheme for fading effect
                legend=None
            )
        )
        st.altair_chart(c2r, use_container_width=True)

    with col2:
        st.markdown("<p style='text-align: center;'>average frequency per profile</p>", unsafe_allow_html=True)
        # Calculate average recency per segment
        avg_f = rfmSegmentation.groupby('profile')['Frequency'].mean().round(0).sort_values(ascending=False)
        avg_f_df = avg_f.reset_index()
        avg_f_df.columns = ['profile', 'avg_f']

        # create the bar chart
        c2f = alt.Chart(avg_f_df).mark_bar().encode(
            y=alt.Y('profile', sort=None, axis=alt.Axis(title=None)),
            x=alt.X('avg_f', axis=alt.Axis(title=None)),
            color=alt.Color('avg_f', scale=alt.Scale(scheme='purples'), legend=None)
        )
        st.altair_chart(c2f, use_container_width=True)

    with col3:
        st.markdown("<p style='text-align: center;'>average monetary value per profile</p>", unsafe_allow_html=True)
        # Calculate average recency per segment
        avg_m = rfmSegmentation.groupby('profile')['MonetaryValue'].mean().round(0).sort_values(ascending=False)
        avg_m_df = avg_m.reset_index()
        avg_m_df.columns = ['profile', 'avg_m']

        # create the bar chart
        c2m = alt.Chart(avg_m_df).mark_bar().encode(
            y=alt.Y('profile', sort=None, axis=alt.Axis(title=None)),
            x=alt.X('avg_m', axis=alt.Axis(title=None)),
            color=alt.Color('avg_m', scale=alt.Scale(scheme='greens'), legend=None)
        )
        st.altair_chart(c2m, use_container_width=True)

    return
