import streamlit as st
import pandas as pd
import json
from apify_scraper import scrape_linkedin_profile, scrape_linkedin_post
import time

st.set_page_config(page_title="LinkedIn Scraper Tool", layout="wide")
st.title("🔗 LinkedIn Scraper Tool (Apify API - No Selenium)")

api_token = st.text_input("🔐 Enter your Apify API Token:", type="password")
cookies_file = st.file_uploader("🍪 Upload your LinkedIn cookies.json", type="json")

url_input = st.text_area("📎 Paste LinkedIn Profile or Post URL(s) (one per line)")
submit = st.button("🚀 Scrape Data")

if submit:
    if not api_token or not cookies_file or not url_input.strip():
        st.warning("⚠️ Please provide API token, cookies.json, and at least one URL.")
    else:
        cookies = json.load(cookies_file)
        urls = [url.strip() for url in url_input.splitlines() if url.strip()]
        all_data = []

        with st.spinner("⏳ Scraping in progress..."):
            for url in urls:
                try:
                    if "/posts/" in url or "/feed/update/" in url:
                        st.info(f"🔍 Scraping Post: {url}")
                        post_data = scrape_linkedin_post(url, api_token, cookies)
                        if not post_data:
                            st.warning(f"⚠️ No data found for Post: {url}")
                        else:
                            df = pd.json_normalize(post_data)
                            st.dataframe(df)
                            all_data.append(df)
                    elif "/in/" in url:
                        st.info(f"👤 Scraping Profile: {url}")
                        profile_data = scrape_linkedin_profile(url, api_token, cookies)
                        if not profile_data:
                            st.warning(f"⚠️ No data found for Profile: {url}")
                        else:
                            df = pd.json_normalize(profile_data)
                            st.dataframe(df)
                            all_data.append(df)
                    else:
                        st.warning(f"⚠️ Skipped unrecognized URL: {url}")

                    # Optional: Add delay between requests to avoid rate limits
                    time.sleep(2)

                except Exception as e:
                    st.error(f"❌ Failed to scrape {url}: {str(e)}")

        if all_data:
            final_df = pd.concat(all_data, ignore_index=True)
            st.success("✅ Scraping completed.")
            st.download_button(
                label="📥 Download Results as Excel",
                data=final_df.to_excel(index=False),
                file_name="linkedin_scraped_data.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
