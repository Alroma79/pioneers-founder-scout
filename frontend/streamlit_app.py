import streamlit as st
import pandas as pd
import os

st.title("Founder Scout")

csv_path = os.path.join("data","candidates.csv")
if os.path.exists(csv_path):
    df = pd.read_csv(csv_path)
    st.dataframe(df)
else:
    st.info("No candidates.csv found. Run backend /search or seed dummy data.")
