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
        matched_urls = []
        platforms_found = []

        try:
            search_results = list(search(query, num_results=search_limit))

            for url in search_results:
                if any(p in url for p in ["yelp.com", "instagram.com", "vagaro.com", "styleseat.com"]):
                    matched_urls.append(url)
                    if "yelp.com" in url:
                        platforms_found.append("Yelp")
                    elif "instagram.com" in url:
                        platforms_found.append("Instagram")
                    elif "vagaro.com" in url:
                        platforms_found.append("Vagaro")
                    elif "styleseat.com" in url:
                        platforms_found.append("StyleSeat")
        except Exception as e:
            search_results = []
            matched_urls = []
            platforms_found = []

        if matched_urls:
            status = "Verified"
        elif search_results:
            status = "Maybe"
        else:
            status = "Not Found"

        results.append({
            "Business Name": name,
            "City": city,
            "Verification Status": status,
            "Found On": ", ".join(set(platforms_found)),
            "Matched URLs": " | ".join(matched_urls)
        })

    result_df = pd.DataFrame(results)

    st.success("✅ Done! Preview below:")
    st.dataframe(result_df)

    csv = result_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Download Verified Listings CSV",
        data=csv,
        file_name="verified_salons.csv",
        mime="text/csv"
    )
