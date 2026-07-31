import requests
from minsearch import Index
import secrets
import string

def generate_short_id(length=8):
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def load_faq_data():
    faq_dataset_url = 'https://raw.githubusercontent.com/anilbhaila/llm-zoomcamp-finalproject/refs/heads/main/data/Ecommerce_FAQ_Chatbot_dataset.json'
    response = requests.get(faq_dataset_url)

    faq_raw = response.json()
    faqs = faq_raw.get("questions")

    documents = []

    for faq in faqs:
        faq["id"] = generate_short_id(8)
        documents.append(faq)

    return(documents)

def build_index(documents):
    index = Index(
        text_fields=['question', 'answer']
    )

    index.fit(documents)
    return index