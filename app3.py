import streamlit as st
from google_play_scraper import reviews
import cohere
import json

# --- Custom CSS for modern style ---
st.markdown("""
    <style>
    body {
        background-color: #0f1117;
        color: #f5f5f5;
    }
    .main {
        background-color: #0f1117;
    }
    .block-container {
        padding-top: 20px;
    }
    h1, h2, h3 {
        color: #f5f5f5;
    }
    .stButton>button {
        background-color: #ff9900;
        color: white;
        border-radius: 8px;
        padding: 0.5em 1.5em;
        border: none;
    }
    .stButton>button:hover {
        background-color: #e88b00;
        color: white;
    }
    .card {
        background-color: #1a1c23;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 0 15px rgba(255, 153, 0, 0.2);
    }
    </style>
""", unsafe_allow_html=True)

# === Cohere API Key ===
COHERE_API_KEY = "4ynfZPaAfQD4L4z6NEwJSWoBlIDltTVMmPtgFeAP"
co = cohere.Client(COHERE_API_KEY)

# === Load app list ===
with open("apps_200.json") as f:
    APP_LIST = json.load(f)

# --- Page config ---
st.set_page_config(page_title="📱 Review Summarizer", layout="wide")
st.title("📱 Review Summarizer")
st.caption("Instantly understand user feedback from Google Play Store apps")

# --- Search and select ---
search_query = st.text_input("🔍 Search for an app by name")
matches = [name for name in APP_LIST.keys() if search_query.lower() in name.lower()]
selected_app = st.selectbox("Select App", matches) if matches else None

# --- Generate button ---
if st.button("✨ Generate Insights") and selected_app:
    app_id = APP_LIST[selected_app]
    st.info(f"Fetching reviews for **{selected_app}** ...")

    result, _ = reviews(app_id, lang='en', country='us', count=100)
    review_texts = [r["content"] for r in result]
    joined_reviews = "\n".join(review_texts)

    with st.spinner("⏳ Generating insights..."):
        summary = co.summarize(
            text=joined_reviews,
            model='summarize-xlarge',
            length='medium',
            format='paragraph'
        ).summary

        positive = co.generate(
            model='command',
            prompt=f"Extract 5 positive customer comments:\n{joined_reviews}",
            max_tokens=300
        ).generations[0].text.strip()

        negative = co.generate(
            model='command',
            prompt=f"Extract 5 negative customer comments:\n{joined_reviews}",
            max_tokens=300
        ).generations[0].text.strip()

        pain_points = co.generate(
            model='command',
            prompt=f"List top customer pain points in bullet points:\n{joined_reviews}",
            max_tokens=300
        ).generations[0].text.strip()

    st.markdown("## 📊 Insights")

    st.markdown(f"<div class='card'><h3>📝 Summary</h3><p>{summary}</p></div>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"<div class='card'><h3>👍 Positive Reviews</h3><p>{positive}</p></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='card'><h3>👎 Negative Reviews</h3><p>{negative}</p></div>", unsafe_allow_html=True)

    st.markdown(f"<div class='card'><h3>⚡ Customer Pain Points</h3><p>{pain_points}</p></div>", unsafe_allow_html=True)

    # --- Download ---
    combined = f"""
    📌 Summary
    {summary}

    👍 Positive Reviews
    {positive}

    👎 Negative Reviews
    {negative}

    ⚡ Customer Pain Points
    {pain_points}
    """

    st.download_button(
        label="💾 Download Insights",
        data=combined,
        file_name=f"{selected_app}_insights.txt",
        mime="text/plain"
    )
