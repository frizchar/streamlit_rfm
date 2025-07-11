import pandas as pd
import streamlit as st
import numpy as np
import plotly.express as px
import altair as alt
from utils import functions as func
from utils import section_function as sxfunc
import random


def run_app(data: pd.DataFrame) -> None:
    st.markdown('<div id="target-section"></div>', unsafe_allow_html=True)

    # generate section title and separating line
    sxfunc.insert_section_title("data", "data_icon.svg")

    # load the data in pandas dataframe format
    df = data

    # ensure proper data types
    df['orderDate'] = pd.to_datetime(df['orderDate'], dayfirst=True)
    # reindex to start from 1
    df.index = np.arange(1, len(df) + 1)
    # name the index
    df.index.name = '#'

    # Create two columns
    col1, col2 = st.columns([2, 1])
    # Display uploaded data in the left column
    with col1:
        df_data = df.copy()
        df_data['orderDate'] = df_data['orderDate'].astype(str).str[:10]
        df_data.index = df_data.index.astype(str)

        st.write("data:")
        st.dataframe(df_data, column_config={r'\#': {'alignment': 'center'}}, height=220)
    # Create a chart using Plotly and display it in the right column
    with col2:
        metadata_dict = {
            '# of rows': len(df),
            '# of columns': df.shape[1],
            '# of missing values': int(df.isnull().any(axis=1).sum()),
            'time period': "[" + min(df['orderDate']).strftime("%d/%m/%Y") + ", " +
                           max(df['orderDate']).strftime("%d/%m/%Y") + "]"
        }

        st.write("metadata:")
        st.json(metadata_dict)

    # generate section title and separating line
    sxfunc.insert_section_title("core KPIs", "kpis_icon.svg")

    # calculate Average Order Value (AOV)
    total_orderValue = df['orderValue'].sum()
    number_of_orders = df['orderID'].nunique()
    aov = total_orderValue / number_of_orders

    # calculate Order Frequency
    number_of_customers = df['customerID'].nunique()
    order_frequency = number_of_orders / number_of_customers

    # calculate Customer Lifetime Value (average total order value per customer)
    clv_per_customer = df.groupby('customerID')['orderValue'].sum()
    clv = clv_per_customer.mean() if not clv_per_customer.empty else 0

    # Display side by side using columns
    col1, col2, col3, col4, col5, col6 = st.columns([1, 1, 1, 1, 2, 1])

    with col1:
        st.metric(label="\# unique customers", value=f"{number_of_customers:,}")

    with col2:
        st.metric(label="\# orders", value=f"{number_of_orders:,}")

    with col3:
        st.metric(label="total order value", value=f"€{total_orderValue:,.2f}")

    with col4:
        st.metric(label="mean order value", value=f"€{aov:,.2f}")

    with col5:
        st.metric(label="order frequency", value=f"{order_frequency:.2f} orders/customer")

    with col6:
        st.metric(label="customer lifetime value", value=f"€{clv:,.2f}")

    # calculate weekly sales
    df_sales = df.copy()
    df_sales['orderDate'] = pd.to_datetime(df_sales['orderDate'])

    # Set orderDate as index for resampling
    df_sales.set_index('orderDate', inplace=True)

    # Resample by week (W-MON means weeks starting on Monday)
    weekly_sales = df_sales['orderValue'].resample('W-MON').sum().reset_index().sort_values('orderDate')

    # Optional: smooth weekly sales with rolling average (e.g., 3 weeks)
    weekly_sales['orderValue_smooth'] = weekly_sales['orderValue'].rolling(window=3, min_periods=1).mean()

    # plot weekly sales
    fig = px.line(
        weekly_sales,
        x='orderDate',
        y='orderValue_smooth',
        title='Weekly Sales (€)',
        labels={'orderDate': 'Week', 'orderValue_smooth': 'ylabel'}
    )

    # remove axis labels
    fig.update_layout(
        xaxis_title='',  # removes the x-axis label
        yaxis_title=''  # removes the y-axis label
    )

    # update line to dashed and add markers (scatter points)
    fig.update_traces(
        line=dict(
            dash='dash',
            color='rgba(0, 0, 255, 0.3)'  # line with 40% opacity
        ),
        mode='lines+markers',
        marker=dict(
            size=10,
            color='rgba(139, 0, 0, 0.6)'  # markers with 60% opacity
        )
    )

    # Center the title and increase font size
    fig.update_layout(
        title=dict(
            text="Weekly Sales [€]",  # Optional: explicitly set title text here
            x=0.5,
            xanchor='center',
            font=dict(
                size=24  # Increase this number to make the title larger
            )
        )
    )

    st.plotly_chart(fig)

    # generate section title and separating line
    sxfunc.insert_section_title("RFM analysis", "rfm_icon.svg")

    st.markdown(
        'RFM analysis is a customer segmentation technique that helps businesses identify and rank their '
        'most valuable customers by examining three key behavioral metrics: Recency, Frequency, and Monetary '
        'value. Recency (R) measures how recently a customer made their last purchase, with more recent '
        'activity indicating higher engagement. Frequency (F) tracks how often a customer makes purchases '
        'within a specific period, highlighting loyal and repeat buyers. Monetary value (M) assesses the '
        'total amount a customer has spent, identifying those who contribute most to revenue.'
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
    rfm.index = np.arange(1, len(rfm) + 1).astype(str)
    # Name the index
    rfm.index.name = '#'

    rfm.rename(columns={
        'orderDate': 'Recency',
        'orderID': 'Frequency',
        'orderValue': 'MonetaryValue'
    }, inplace=True)

    st.write("RFM metrics:")
    st.dataframe(rfm)

    # generate section title and separating line
    sxfunc.insert_section_title("profile analysis", "profiles_icon.svg")

    st.markdown(
        '<div style="line-height:1.5; margin:0; padding:0;">Each customer '
        'gets scored from 1 (highest score) to 4 (least score) for each metric [R,F and M]. '
        '<br>The scores are calculated as quartiles of the distribution of each metric.'
        '<br>The combined RFM scores allow businesses to profile (segment) customers for targeted '
        'marketing and retention strategies.<br> <br><div>',
        unsafe_allow_html=True
    )

    quantiles = rfm[['Recency', 'Frequency', 'MonetaryValue']].quantile(q=[0.25, 0.5, 0.75])
    # st.write("RFM dtypes:")
    # st.dataframe(rfm.dtypes)
    st.write("RFM quantiles:")
    st.dataframe(quantiles, width=400)

    # create the RFM segmentation table
    rfmSegmentation = rfm


    rfmSegmentation['R_Quartile'] = rfmSegmentation['Recency'].apply(func.RClass, args=('Recency', quantiles,))
    rfmSegmentation['F_Quartile'] = rfmSegmentation['Frequency'].apply(func.FMClass, args=('Frequency', quantiles,))
    rfmSegmentation['M_Quartile'] = rfmSegmentation['MonetaryValue'].apply(func.FMClass,
                                                                           args=('MonetaryValue', quantiles,))

    rfmSegmentation['RFMClass'] = rfmSegmentation.R_Quartile.map(str) \
                                  + rfmSegmentation.F_Quartile.map(str) \
                                  + rfmSegmentation.M_Quartile.map(str)

    # Add column B using map
    rfmSegmentation['profile'] = rfmSegmentation['RFMClass'].apply(func.rfm_segment)

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

        st.markdown("<p style='text-align: center;'>mean monetary value [€]</p>", unsafe_allow_html=True)
        # pivot the data to get the mean monetary value for each R-F combination
        rfm_pivot = rfmSegmentation.groupby(['R_Quartile', 'F_Quartile'])['MonetaryValue'].mean().round(0).reset_index()

        # create the mean monetary value heatmap
        heatmap = alt.Chart(rfm_pivot).mark_rect().encode(
            x=alt.X('F_Quartile:O', title='Frequency score', axis=alt.Axis(labelAngle=0)),
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
        st.markdown("<p style='text-align: center;'>mean recency per profile</p>", unsafe_allow_html=True)
        # Calculate average recency per segment
        avg_r = rfmSegmentation.groupby('profile')['Recency'].mean().round(0).sort_values(ascending=True)
        avg_r_df = avg_r.reset_index()
        avg_r_df.columns = ['profile', 'avg_r']

        # create the bar chart
        c2r = alt.Chart(avg_r_df).mark_bar(size=20).encode(
            y=alt.Y('profile', sort=None),
            x=alt.X('avg_r', axis=alt.Axis(title=None)),
            color=alt.Color('avg_r', scale=alt.Scale(scheme='reds', reverse=True), legend=None)
        ).properties(height=200)
        st.altair_chart(c2r, use_container_width=True)

    with col2:
        st.markdown("<p style='text-align: center;'>mean frequency per profile</p>", unsafe_allow_html=True)
        # Calculate average recency per segment
        avg_f = rfmSegmentation.groupby('profile')['Frequency'].mean().round(0).sort_values(ascending=False)
        avg_f_df = avg_f.reset_index()
        avg_f_df.columns = ['profile', 'avg_f']

        # create the bar chart
        c2f = alt.Chart(avg_f_df).mark_bar(size=20).encode(
            y=alt.Y('profile', sort=None, axis=alt.Axis(title=None)),
            x=alt.X('avg_f', axis=alt.Axis(title=None)),
            color=alt.Color('avg_f', scale=alt.Scale(scheme='purples'), legend=None)
        ).properties(height=200)
        st.altair_chart(c2f, use_container_width=True)

    with col3:
        st.markdown("<p style='text-align: center;'>mean monetary value per profile [€]</p>", unsafe_allow_html=True)
        # Calculate average recency per segment
        avg_m = rfmSegmentation.groupby('profile')['MonetaryValue'].mean().round(0).sort_values(ascending=False)
        avg_m_df = avg_m.reset_index()
        avg_m_df.columns = ['profile', 'avg_m']

        # create the bar chart
        c2m = alt.Chart(avg_m_df).mark_bar(size=20).encode(
            y=alt.Y('profile', sort=None, axis=alt.Axis(title=None)),
            x=alt.X('avg_m', axis=alt.Axis(title=None)),
            color=alt.Color('avg_m', scale=alt.Scale(scheme='greens'), legend=None)
        ).properties(height=200)
        st.altair_chart(c2m, use_container_width=True)

    # generate section title and separating line
    sxfunc.insert_section_title("customer retention analysis", "retention_icon.svg")

    st.markdown(
        '<div style="line-height:1.5; margin:0; padding:0;">We calculate '
        'the monthly retention rate.<br> <br><div>',
        unsafe_allow_html=True
    )

    # Extract year-month for grouping
    df['orderMonth'] = df['orderDate'].dt.to_period('M')

    # Group by customer and month to get unique customers per month
    monthly_customers = df.groupby('orderMonth')['customerID'].apply(set).sort_index()

    # Initialize a list to store retention rates
    retention_rates = []

    # Iterate over months starting from the second month
    months = monthly_customers.index

    for i in range(1, len(months)):
        current_month = months[i]
        prev_month = months[i - 1]

        customers_current = monthly_customers[current_month]
        customers_prev = monthly_customers[prev_month]

        # Calculate how many customers from prev month ordered again in current month
        retained_customers = customers_current.intersection(customers_prev)

        # Retention rate formula
        if len(customers_prev) > 0:
            retention_rate = len(retained_customers) / len(customers_prev) * 100
        else:
            retention_rate = None  # or 0 or np.nan if no customers in prev month

        retention_rates.append({
            'Year - Month': current_month.to_timestamp(),
            'Retention Rate [%]': round(retention_rate, 1)
        })

    # Convert to DataFrame for better visualization
    retention_df = pd.DataFrame(retention_rates)
    # retention_df.drop(index=df.index[0], inplace=True)  # get rid of first month of dataset since it has no retention
    retention_df['Year - Month'] = retention_df['Year - Month'].astype(str).str[:7]
    retention_df.index = np.arange(1, len(retention_df) + 1)
    retention_df.index.name = '#'
    retention_df.index = retention_df.index.astype(str)

    # create two columns
    col1, col2 = st.columns([1, 3])
    with col1:
        st.dataframe(retention_df, column_config={r'\#': {'alignment': 'center'}}, height=400)
    with col2:

        # plot weekly sales
        fig22 = px.line(
            retention_df,
            x='Year - Month',
            y='Retention Rate [%]',
            title='Retention Rate [%]',
            labels={'Year - Month': 'Year - Month', 'Retention Rate [%]': 'Retention Rate [%]'}
        )

        # remove axis labels
        fig22.update_layout(
            xaxis_title='',  # removes the x-axis label
            yaxis_title=''  # removes the y-axis label
        )

        # update line to dashed and add markers (scatter points)
        fig22.update_traces(
            line=dict(
                dash='dash',
                color='rgba(0, 0, 255, 0.3)'  # line with 40% opacity
            ),
            mode='lines+markers',
            marker=dict(
                size=10,
                color='rgba(139, 0, 0, 0.6)'  # markers with 60% opacity
            )
        )

        # Center the title and increase font size
        fig22.update_layout(
            title=dict(
                text="Monthly Retention Rate [%]",  # Optional: explicitly set title text here
                x=0.5,
                xanchor='center',
                font=dict(
                    size=24  # Increase this number to make the title larger
                )
            )
        )

        st.plotly_chart(fig22)

    # generate section title and separating line
    sxfunc.insert_section_title("insights & recommended marketing strategies", "insights_icon.svg")

    st.subheader(":blue[_handling top-tier customers:_]")

    count_champions = counts_df.loc[counts_df['profile'] == 'champion', '# customers'].iloc[0]
    count_champions_perce = 100*count_champions/number_of_customers

    st.markdown(
        f"{count_champions} out of {number_of_customers} customers ({count_champions_perce:.1f}%) "
        f"{random.choice(['constitute','fall into'])} the '_champion_' segment, namely loyal brand advocates "
        f"who {random.choice(['do better than','outperform'])} other customers across "
        f"all metrics (_RFM_)."
        f"<br> This group represents {random.choice(['core revenue drivers','high lifetime value customers'])} "
        f"who should be prioritized for loyalty rewards and exclusive offers to maximize retention.",
        unsafe_allow_html = True
    )

    st.subheader(":blue[_upselling and cross-selling:_]")

    count_potential_loyalist = counts_df.loc[counts_df['profile'] == 'potential_loyalist', '# customers'].iloc[0]
    count_potential_loyalist_perce = 100*count_potential_loyalist/number_of_customers

    st.markdown(
        f"{count_potential_loyalist} out of {number_of_customers} customers ({count_potential_loyalist_perce:.1f}%) fall "
        f"into the '_potential loyalist_' segment, that comprises of high-frequency customers who spend moderately."
        f"<br> This type of customers may be nudged to increase average order value by recommending complementary products, "
        f"<br> thus boosting further conversion rates.",
        unsafe_allow_html = True
    )

    st.subheader(":blue[_targeted reactivation:_]")

    count_about_to_sleep = counts_df.loc[counts_df['profile'] == 'about_to_sleep', '# customers'].iloc[0]
    count_about_to_sleep_perce = 100*count_about_to_sleep/number_of_customers

    st.markdown(
        f"{count_about_to_sleep} out of {number_of_customers} customers ({count_about_to_sleep_perce:.1f}%) fall "
        f"into the '_about to sleep_' segment, indicating a significant group at risk of churn. "
        f"<br> This suggests an opportunity to deploy reactivation "
        f"campaigns such as special discounts or personalized emails to win them back."
        f"<br> Customers classified as '_about to sleep_' respond well to personalized win-back "
        f"campaigns offering discounts, resulting in improved reactivation rates.",
        unsafe_allow_html = True
    )

    return
