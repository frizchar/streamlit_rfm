import streamlit as st
import base64
import os


def insert_section_title(section_title, icon_file):
    # Function to load SVG and encode it as base64
    def svg_to_base64(svg_path):
        with open(svg_path, "r") as f:
            svg_content = f.read()
        b64 = base64.b64encode(svg_content.encode("utf-8")).decode("utf-8")
        return b64

    script_dir = os.path.dirname(os.path.abspath(__file__))
    svg_path = os.path.join(script_dir, "..", "assets", icon_file)
    svg_path = os.path.normpath(svg_path)  # normalize path separators

    # Encode your SVG icon
    svg_b64 = svg_to_base64(svg_path)

    # Create HTML with SVG image inline with title text
    html_title = f"""
    <div style="display: flex; justify-content: center; align-items:center;">
        <img src="data:image/svg+xml;base64,{svg_b64}" style="height: 40px; margin-right: 10px; margin-bottom: -5px;" />
        <h2 style="margin: 0; font-weight: bold; text-align: center">{section_title}</h2>
    </div>
    """

    # Render the HTML in Streamlit with unsafe_allow_html=True
    st.markdown(html_title, unsafe_allow_html=True)

    # insert line
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

    return
