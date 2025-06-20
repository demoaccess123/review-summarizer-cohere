import streamlit as st
from google_play_scraper import reviews
import cohere
import json

# === Your Cohere API Key ===
COHERE_API_KEY = "4ynfZPaAfQD4L4z6NEwJSWoBlIDltTVMmPtgFeAP"
co = cohere.Client(COHERE_API_KEY)

with open("apps_200.json") as f:
    APP_LIST = json.load(f)

st.set_page_config(page_title="Play Store Review Insights", layout="wide")
st.title("📱 Google Play Review Insights")

# --- Search box with suggestions ---
search_query = st.text_input("🔍 Search for an app by name")

matches = [name for name in APP_LIST.keys() if search_query.lower() in name.lower()]
selected_app = st.selectbox("Select App", matches) if matches else None

if st.button("Generate Insights") and selected_app:
    app_id = APP_LIST[selected_app]
    st.info(f"Fetching reviews for **{selected_app}** (ID: {app_id})...")

    result, _ = reviews(app_id, lang='en', country='us', count=100)
    review_texts = [r["content"] for r in result]

    joined_reviews = "\n".join(review_texts)

    with st.spinner("🔄 Generating insights using Cohere..."):
        # --- Summary ---
        summary_response = co.summarize(
            text=joined_reviews,
            model='summarize-xlarge',
            length='medium',
            format='paragraph'
        ).summary

        # --- Positive Reviews ---
        pos_response = co.generate(
            model='command',
            prompt=f"Extract 5 positive customer comments from the following reviews:\n{joined_reviews}",
            max_tokens=300
        ).generations[0].text.strip()

        # --- Negative Reviews ---
        neg_response = co.generate(
            model='command',
            prompt=f"Extract 5 negative customer comments from the following reviews:\n{joined_reviews}",
            max_tokens=300
        ).generations[0].text.strip()

        # --- Customer Pain Points (bulleted) ---
        pain_response = co.generate(
            model='command',
            prompt=f"List the top customer pain points in bullet points from the following reviews:\n{joined_reviews}",
            max_tokens=300
        ).generations[0].text.strip()

    # --- Layout ---
    st.subheader("📝 Summary")
    st.success(summary_response)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("👍 Positive Reviews")
        st.info(pos_response)

    with col2:
        st.subheader("👎 Negative Reviews")
        st.warning(neg_response)

    st.subheader("⚡ Customer Pain Points")
    st.error(pain_response)
