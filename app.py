import streamlit as st
import pandas as pd
import requests
from googlesearch import search

st.set_page_config(page_title="BHSG Listing Verifier", layout="wide")
st.title("🔍 BHSG Listing Verifier")

st.markdown("""
Upload a CSV with the following columns (case-insensitive):
- `Title` (will be renamed to Business Name)
- `Google Address`
- `Location`

This app will perform Google searches for each business and check for presence on:
- Yelp
- Instagram
- Vagaro
- StyleSeat

Returns a verification status and matched URLs.
""")

uploaded_file = st.file_uploader("Upload your salon CSV", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    df = df.fillna("")

    # Normalize and rename columns
    df.columns = df.columns.str.strip().str.lower()
    df = df.rename(columns={
        "title": "business name",
        "google address": "address",
        "location": "city"
    })

    results = []
    search_limit = 5

    st.write("🔄 Running checks... this may take a moment.")

    for index, row in df.iterrows():
        name = row["business name"]
        city = row["city"]

        query = f"{name} {city} hair salon"
        try:
