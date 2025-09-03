import streamlit as st
import pandas as pd
import requests
from googlesearch import search
import os
from datetime import datetime

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

Returns a verification status, matched URLs, platform count, and timestamp.
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
    verification_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    st.write("🔄 Running checks... this may take a moment.")

    for index, row in df.iterrows():
        name = row["business name"]
        city = row["city"]

        query = f"{name} {city} hair salon"
        yelp_url = ""
        instagram_url = ""
        vagaro_url = ""
        styleseat_url = ""
        platforms_found = []

        try:
            search_results = list(search(query, num_results=search_limit))

            for url in search_results:
                if "yelp.com" in url and not yelp_url:
                    yelp_url = url
                    platforms_found.append("Yelp")
                elif "instagram.com" in url and not instagram_url:
                    instagram_url = url
                    platforms_found.append("Instagram")
                elif "vagaro.com" in url and not vagaro_url:
                    vagaro_url = url
                    platforms_found.append("Vagaro")
                elif "styleseat.com" in url and not styleseat_url:
                    styleseat_url = url
                    platforms_found.append("StyleSeat")
        except Exception as e:
            search_results = []

        if any([yelp_url, instagram_url, vagaro_url, styleseat_url]):
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
            "Platform Count": len(set(platforms_found)),
            "Yelp URL": yelp_url,
            "Instagram URL": instagram_url,
            "Vagaro URL": vagaro_url,
            "StyleSeat URL": styleseat_url,
            "Verified At": verification_time
        })

    result_df = pd.DataFrame(results)

    st.success("✅ Done! Preview below:")

    filter_option = st.selectbox("Filter by Verification Status", ["All"] + sorted(result_df["Verification Status"].unique()))
    if filter_option != "All":
        filtered_df = result_df[result_df["Verification Status"] == filter_option]
    else:
        filtered_df = result_df

    st.dataframe(filtered_df)

    original_filename = os.path.splitext(uploaded_file.name)[0]
    output_filename = f"{original_filename}_verified_salons.csv"

    csv = result_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Download Verified Listings CSV",
        data=csv,
        file_name=output_filename,
        mime="text/csv"
    )
