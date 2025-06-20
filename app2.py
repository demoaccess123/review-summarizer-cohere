import streamlit as st
from google_play_scraper import reviews
import cohere
import json

# --- Custom Modern CSS with subtle fade-in animation ---
st.markdown("""
    <style>
    /* Page background */
    body {
        background: linear-gradient(to right, #f8f9fa, #e9ecef);
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    }
    /* Main container */
    .main {
        background-color: #ffffff;
        border-radius: 10px;
        padding: 30px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        animation: fadeIn 1s ease-in;
    }
    /* Headings */
    h1, h2, h3 {
        color: #333333;
    }
    /* Buttons */
    .stButton>button {
        background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);
        color: white;
        border: none;
        border-radius: 5px;
    }
    .stButton>button:hover {
        background: linear-gradient(90deg, #43e97b 0%, #38f9d7 100%);
    }
    /* Info boxes */
    .stAlert {
        border-radius: 10px;
        padding: 20px;
        margin-top: 10px;
    }
    /* Download button */
    .stDownloadButton>button {
        background: linear-gradient(90deg, #f7971e 0%, #ffd200 100%);
        color: black;
        font-weight: bold;
        border-radius: 5px;
    }
    /* Fade-in animation */
    @keyframes fadeIn {
        0% {opacity: 0;}
        100% {opacity: 1;}
    }
    </style>
""", unsafe_allow_html=True)

# === Cohere API Key ===
COHERE_API_KEY = "4ynfZPaAfQD4L4z6NEwJSWoBlIDltTVMmPtgFeAP"
co = cohere.Client(COHERE_API_KEY)

# Load app list
with open("apps_200.json") as f:
    APP_LIST = json.load(f)

# --- Page config ---
st.set_page_config(page_title="🚀 Play Store Review Insights", layout="wide")
st.title("🚀 Google Play Review Insights")

# --- Search and select ---
search_query = st.text_input("🔍 Search for an app by name")
matches = [name for name in APP_LIST.keys() if search_query.lower() in name.lower()]
selected_app = st.selectbox("Select App", matches) if matches else None

# --- Generate Insights ---
if st.button("✨ Generate Insights") and selected_app:
    app_id = APP_LIST[selected_app]
    st.info(f"Fetching reviews for **{selected_app}** (ID: `{app_id}`)...")

    result, _ = reviews(app_id, lang='en', country='us', count=100)
    review_texts = [r["content"] for r in result]
    joined_reviews = "\n".join(review_texts)

    with st.spinner("🔮 Generating insights using Cohere AI..."):
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
            prompt=f"Extract 5 positive customer comments:\n{joined_reviews}",
            max_tokens=300
        ).generations[0].text.strip()

        # --- Negative Reviews ---
        neg_response = co.generate(
            model='command',
            prompt=f"Extract 5 negative customer comments:\n{joined_reviews}",
            max_tokens=300
        ).generations[0].text.strip()

        # --- Customer Pain Points ---
        pain_response = co.generate(
            model='command',
            prompt=f"List top customer pain points as bullet points:\n{joined_reviews}",
            max_tokens=300
        ).generations[0].text.strip()

    # --- Stylish Layout ---
    st.markdown("---")
    st.header("📌 Insights")

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

    # --- Download Button ---
    download_text = f"""
📌 **Summary**
{summary_response}

👍 **Positive Reviews**
{pos_response}

👎 **Negative Reviews**
{neg_response}

⚡ **Customer Pain Points**
{pain_response}
    """
    st.download_button(
        label="💾 Download Insights",
        data=download_text,
        file_name=f"{selected_app}_insights.txt",
        mime="text/plain"
    )
