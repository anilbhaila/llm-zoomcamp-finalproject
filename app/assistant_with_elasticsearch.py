import sys

from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

from ingest import load_faq_data, build_index
from rag_with_elasticsearch import RAGWithElasticSearch
from db_save import save_conversation

from elasticsearch import Elasticsearch

import spacy
import numpy as np
import socket
import requests

def get_elasticsearch_url():
    try:
        socket.getaddrinfo("elasticsearch", None)
        host = "elasticsearch"
    except socket.gaierror:
        # Fallback to local machine if Docker network host isn't found
        host = "localhost"
    
    try:
        url = f'http://{host}:9200'
        print(url)

        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return url
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to Elasticsearch service: {e}")
        return None   

def create_assistant(search_type="text"):
    load_dotenv()

    nlp = spacy.load('en_core_web_sm')
    es_client = Elasticsearch(get_elasticsearch_url())
    return RAGWithElasticSearch(
        embedder=nlp,
        search_client=es_client,
        search_type=search_type,
        llm_client=OpenAI(),
    )

if __name__ == "__main__":
    assistant = create_assistant()

    query = "How to create my account?"
    if len(sys.argv) > 1:
        query = sys.argv[1]

    answer = assistant.rag(query)
    print(answer)

    save_conversation(assistant.last_call, query)