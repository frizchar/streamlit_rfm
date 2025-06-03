# streamlit_rfm
### Overview
Customer analytics app (hosted [here](https://castoma.streamlit.app/)) based on customer transactional data.

### App features
* core customer KPIs
* customer segmentation via [RFM analysis](https://en.wikipedia.org/wiki/RFM_(market_research))
* generation of insights and recommended marketing strategies

### Folder structure
 ```
streamlit_rfm/
├── main.py                  # main entry point for the app
├── requirements.txt         # required packages
├── .streamlit/
│   └── config.toml          # streamlit theme configuration
├── assets/
│   └── castoma.svg          # svg file
│   └── data_icon.svg        # svg file
│   └── kpis_icon.svg        # svg file
│   └── profiles_icon.svg    # svg file
│   └── rfm_icon.svg         # svg file
│   └── insights_icon.svg    # svg file
│   └── favicon.ico          # favicon file
│   └── sample_data.toml     # sample data file
├── utils/
│   └── engine.py            # engine module
│   └── functions.py         # functions module
│   └── section_function.py  # section title module
 ```

### Dependencies
The required packages are included in file ```requirements.txt```.<br>
Python interpreter version used for this project: **3.9.4**
