import streamlit as st
from google_play_scraper import reviews
import cohere
import json

# === Config ===
st.set_page_config(
    page_title="Review Summarizer",
    layout="wide",
    page_icon="💬"
)

# === Cohere API ===
co = cohere.Client("4ynfZPaAfQD4L4z6NEwJSWoBlIDltTVMmPtgFeAP")

# === Load Apps List ===
with open("apps_200.json") as f:
    APP_LIST = json.load(f)

# === Custom CSS & Hero ===
st.markdown("""
    <style>
    body {
        background: #f5f7fa;
        font-family: 'Helvetica Neue', sans-serif;
    }
    .hero {
        background: linear-gradient(rgba(0,0,0,0.4), rgba(0,0,0,0.4)),
                    url('https://images.unsplash.com/photo-1581090700227-4c4f50b12731?ixlib=rb-4.0.3&auto=format&fit=crop&w=1470&q=80');
        background-size: cover;
        background-position: center;
        border-radius: 10px;
        padding: 100px 30px;
        text-align: center;
        color: white;
    }
    .hero h1 {
        font-size: 3em;
        margin-bottom: 10px;
    }
    .hero p {
        font-size: 1.2em;
        margin-bottom: 30px;
    }
    .search-box input {
        width: 40%;
        padding: 12px;
        border-radius: 5px;
        border: none;
    }
    .stButton>button {
        background-color: #f9a825;
        color: black;
        border: none;
        border-radius: 5px;
        padding: 10px 20px;
        font-weight: bold;
    }
    .card {
        background: white;
        padding: 30px;
        border-radius: 10px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    }
    </style>
""", unsafe_allow_html=True)

# === HERO ===
st.markdown("""
    <div class="hero">
        <h1>📱 Review Summarizer</h1>
        <p>Instantly understand user feedback from Google Play Store apps</p>
    </div>
""", unsafe_allow_html=True)

# === Search ===
st.markdown("<br>", unsafe_allow_html=True)
search_query = st.text_input("🔍 Search for an app by name")
matches = [name for name in APP_LIST.keys() if search_query.lower() in name.lower()]
selected_app = st.selectbox("Select App", matches) if matches else None

# === Button ===
if st.button("✨ Generate Insights") and selected_app:
    app_id = APP_LIST[selected_app]
    st.info(f"Fetching reviews for **{selected_app}** ...")

    result, _ = reviews(app_id, lang='en', country='us', count=100)
    review_texts = [r["content"] for r in result]
    joined_reviews = "\n".join(review_texts)

    with st.spinner("💡 Summarizing reviews..."):
        # --- Summary
        summary = co.summarize(
            text=joined_reviews,
            model='summarize-xlarge',
            length='medium',
            format='paragraph'
        ).summary

        # --- Positive
        positive = co.generate(
            model='command',
            prompt=f"Extract 5 positive comments:\n{joined_reviews}",
            max_tokens=300
        ).generations[0].text.strip()

        # --- Negative
        negative = co.generate(
            model='command',
            prompt=f"Extract 5 negative comments:\n{joined_reviews}",
            max_tokens=300
        ).generations[0].text.strip()

        # --- Pain Points
        pain_points = co.generate(
            model='command',
            prompt=f"List main pain points as bullet points:\n{joined_reviews}",
            max_tokens=300
        ).generations[0].text.strip()

    # === Display in Beautiful Cards ===
    st.markdown("## 📊 Insights")

    st.markdown(f"""
        <div class="card">
            <h3>📝 Summary</h3>
            <p>{summary}</p>
        </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"""
            <div class="card">
                <h3>👍 Positive Reviews</h3>
                <p>{positive}</p>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
            <div class="card">
                <h3>👎 Negative Reviews</h3>
                <p>{negative}</p>
            </div>
        """, unsafe_allow_html=True)

    st.markdown(f"""
        <div class="card">
            <h3>⚡ Customer Pain Points</h3>
            <p>{pain_points}</p>
        </div>
    """, unsafe_allow_html=True)

    # === Download Button ===
    download_text = f"""
    📌 **Summary**
    {summary}

    👍 **Positive Reviews**
    {positive}

    👎 **Negative Reviews**
    {negative}

    ⚡ **Customer Pain Points**
    {pain_points}
    """
    st.download_button(
        label="💾 Download Insights",
        data=download_text,
        file_name=f"{selected_app}_insights.txt",
        mime="text/plain"
    )
