import requests
from bs4 import BeautifulSoup
from sentence_transformers import SentenceTransformer, util
from transformers import pipeline
import os

# Set your actual SerpAPI key here
SERPAPI_KEY = "YOUR_SERPAPI_KEY"  # Replace with your actual SerpAPI key
os.environ["SERPAPI_KEY"] = "Your_Key_goes_here"


def check_facts(text: str) -> int:
    """
    Cross-checks text against Google Fact Check API.
    Returns a score between 0-100 indicating factual reliability.
    """
    api_url = f"https://toolbox.google.com/factcheck/api/v1/claimsearch?query={text[:200]}"
    try:
        response = requests.get(api_url)
        data = response.json()
        if "claims" in data and data["claims"]:
            return 80  # If found in fact-checking database
        return 40  # No verification found
    except:
        return 50  # Default uncertain score

def check_google_scholar(url: str) -> int:
    """
    Fetches citation count from Google Scholar using SerpAPI.
    """
    serp_api_url = f"https://serpapi.com/search.json?q=site:{url}&engine=google_scholar"
    try:
        response = requests.get(serp_api_url)
        data = response.json()
        citation_count = data.get("organic_results", [{}])[0].get("cited_by", {}).get("value", 0)
        return citation_count
    except:
        return 0

def rate_url_validity(user_query: str, url: str) -> dict:
    """
    Evaluates the validity of a given URL by computing various metrics including
    domain trust, content relevance, fact-checking, bias, and citation scores.
    """
    # Fetch page content
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    page_text = soup.get_text()

    # Step 1: Domain Trust (Placeholder, assume 70 for now)
    domain_trust = 70

    # Step 2: Content Relevance
    model = SentenceTransformer('all-MiniLM-L6-v2')
    similarity_score = util.pytorch_cos_sim(
        model.encode(user_query, convert_to_tensor=True),
        model.encode(page_text[:512], convert_to_tensor=True)
    ).item() * 100

    # Step 3: Fact-Checking
    fact_check_score = check_facts(page_text[:512])

    # Step 4: Bias Detection (Placeholder using Sentiment Analysis)
    sentiment_pipeline = pipeline("text-classification", model="cardiffnlp/twitter-roberta-base-sentiment")
    sentiment_result = sentiment_pipeline(page_text[:512])[0]
    bias_score = 100 if sentiment_result["label"] == "POSITIVE" else 50 if sentiment_result["label"] == "NEGATIVE" else 75

    # Step 5: Citation Check
    citation_count = check_google_scholar(url)
    citation_score = min(citation_count * 10, 100)  # Normalize

    # Step 6: Compute Final Validity Score
    final_score = (
        (0.3 * domain_trust) +
        (0.3 * similarity_score) +
        (0.2 * fact_check_score) +
        (0.1 * bias_score) +
        (0.1 * citation_score)
    )

    return {
        "Domain Trust": domain_trust,
        "Content Relevance": similarity_score,
        "Fact-Check Score": fact_check_score,
        "Bias Score": bias_score,
        "Citation Score": citation_score,
        "Final Validity Score": final_score
    }
user_prompt = "I have just been on an international flight, can I come back home to hold my 1-month-old newborn?"
url_to_check = "https://www.bhtp.com/blog/when-safe-to-travel-with-newborn/"
result = rate_url_validity(user_prompt, url_to_check)
print(result)