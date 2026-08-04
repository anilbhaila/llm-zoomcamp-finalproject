import requests
import secrets
import string
import json

from pathlib import Path
from minsearch import Index


def generate_short_id(length=8):
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def load_faq_data():
    
    file_path = Path("../data/EcommerceFAQWithIds.json")

    documents = []

    if file_path.exists():
        with open(file_path, "r", encoding="utf-8") as file:
            documents = json.load(file)

        print("Existing Ecommerce FAQ With Ids loaded Successfully!!")
        print(f"Document Size:{len(documents)}")
    else:
        faq_dataset_url = 'https://raw.githubusercontent.com/anilbhaila/llm-zoomcamp-finalproject/refs/heads/main/data/Ecommerce_FAQ_Chatbot_dataset.json'
        response = requests.get(faq_dataset_url)

        faq_raw = response.json()
        faqs = faq_raw.get("questions")

        for faq in faqs:
            faq["id"] = generate_short_id(8)
            documents.append(faq)

        with open("../data/EcommerceFAQWithIds.json", "w") as file:
            json.dump(documents, file, indent=4)
            print("Ecommerce FAQ With Ids Generated Successfully!!")

    return documents

def build_index(documents):
    index = Index(
        text_fields=['question', 'answer']
    )

    index.fit(documents)
    return index