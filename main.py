import streamlit as st
import pandas as pd
import os
import tomli
from utils import engine

st.set_page_config(
    page_title="castoma",  # Title displayed in the browser tab
    page_icon="assets/favicon.ico",
    layout="wide"
)

# insert logo, source: https://www.svgrepo.com/
working_directory = os.getcwd()
relative_path = "assets/castoma.svg"
full_path = os.path.join(working_directory, relative_path)

with open(full_path, "r") as f:
    svg_content = f.read()

# Display the SVG
st.image(svg_content, width=80)


def load_sample_toml():
    try:
        with open("assets/sample_data.toml", "rb") as f:
            sample_data_dict = tomli.load(f)

        if isinstance(sample_data_dict, dict):
            return pd.DataFrame(sample_data_dict)
        return None
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None


def main():
    # st.title("customer segmentation::RFM analysis")
    st.markdown(
        "<h1 style='font-size:30px;'>"
        "<span style='color:#E67300;'>castoma</span> :: transform transactional data into consumer insights"
        "</h1>",
        unsafe_allow_html=True
    )

    st.markdown(
        '<div style="line-height:1.5; margin:0; padding:0;">employing marketing analytics '
        'to develop customer-behavior'
        ' profiles based on past consumer data<br>castoma implements customer segmentation'
        ' via RFM analysis<br><br>try out the app with sample data</div>',
        unsafe_allow_html=True
    )

    st.markdown("""or upload your own .csv file with this column layout: `[customerID, orderDate, orderID, orderValue]`""")

    df = None

    # sample data section first
    if st.button("run castoma with sample data"):
        df = load_sample_toml()
        if df is not None:
            st.success("sample data loaded")

    # file upload section second
    uploaded_file = st.file_uploader("Or upload your own CSV file", type="csv")

    # apply custom CSS to adjust the width
    css = '''
    <style>
    [data-testid='stFileUploader'] {
        width: 520px; /* Adjust the width as needed */
    }
    </style>
    '''
    st.markdown(css, unsafe_allow_html=True)

    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            st.success("external data loaded")
        except Exception as e:
            st.error(f"CSV Error: {str(e)}")

    # run app engine
    if df is not None:
        engine.run_app(df)


if __name__ == "__main__":
    main()
