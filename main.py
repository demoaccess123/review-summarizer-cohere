import cohere
from google_play_scraper import Sort, reviews
import os

# Replace this with your actual Cohere API key
COHERE_API_KEY = "4ynfZPaAfQD4L4z6NEwJSWoBlIDltTVMmPtgFeAP"
client = cohere.Client(COHERE_API_KEY)

def fetch_reviews(app_id, num_reviews=100):
    result, _ = reviews(
        app_id,
        lang='en',
        country='us',
        sort=Sort.NEWEST,
        count=num_reviews
    )
    return [r['content'] for r in result]

def summarize_reviews(reviews_list):
    joined_reviews = "\n".join(reviews_list[:100])
    response = client.summarize(text=joined_reviews)
    return response.summary

if __name__ == "__main__":
    print("Fetching reviews...")
    reviews_list = fetch_reviews("com.king.candycrushsaga")
    print("Summarizing...")
    summary = summarize_reviews(reviews_list)
    print("\n📄 Summary:")
    print(summary)
