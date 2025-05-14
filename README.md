# streamlit_rfm
### Overview
Customer analytics app (hosted [here](https://castoma.streamlit.app/)).

App features:
* core KPIs of customer transactional data
* customer segmentation via [RFM analysis](https://en.wikipedia.org/wiki/RFM_(market_research)) 

### Folder structure
 ```
streamlit_rfm/
├── main.py               # main entry point for the app
├── requirements.txt      # required packages
├── .streamlit/
│   └── config.toml       # streamlit theme configuration
├── assets/
│   └── castoma.svg       # svg file
│   └── favicon.ico       # favicon file
│   └── sample_data.toml  # sample data file
├── utils/
│   └── engine.py         # engine module
│   └── functions.py      # functions module
 ```

### Dependencies
The required packages are included in file ```requirements.txt```.<br>
Python interpreter version used for this project: **3.9.4**
