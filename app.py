import streamlit as st

st.set_page_config(
    page_title="Streamlit App Template",
    page_icon="📊",
    layout="centered",
)

st.title("Streamlit App Template")
st.write(
    "Welcome! This is a minimal multi-page Streamlit app template. "
    "Use the navigation in the sidebar to switch between pages."
)

st.markdown(
    """
### What’s in this app?

- **Overview** – explains what the app is about  
- **Data Explorer** – shows an example dataset and simple chart  
- **About** – info about the project / authors  

You can use this as a starting point for your own projects or for teaching.
"""
)

st.info(
    "Tip: open the `pages/` folder in your editor to see how each page is defined."
)

