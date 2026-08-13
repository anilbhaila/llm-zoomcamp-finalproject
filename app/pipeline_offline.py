import sys
import pandas as pd
import requests
import re

from pathlib import Path
from typing import Dict, List, Union
import spacy
import numpy as np
import socket
import json

from sentence_transformers import SentenceTransformer
from elasticsearch import Elasticsearch

def load_data(*args, **kwargs):
    """
    Extract data from URL. 
    
    """
    url = "https://raw.githubusercontent.com/anilbhaila/llm-zoomcamp-finalproject/refs/heads/main/data/Ecommerce_FAQ_Chatbot_dataset.json"  
    
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        json_data = response.json()

        faqs = json_data.get("questions")
        # Create a DataFrame
        df = pd.DataFrame(list(faqs))

        return df
    except Exception as e:
        print(f"An error occurred while reading the CSV file: {e}")
        return None

def transformToAddChunk(data: pd.DataFrame, *args, **kwargs):
    """
    Template code for a transformer block to add Chunk.

    """
    # Specify your transformation logic here

    rowNumber = 0
    documents = []

    for _, row in data.iterrows():
        number = str(rowNumber)
        rowNumber+=1
        question = str(row['question'])
        answer = str(row['answer'])

        sanitized_question = re.sub(r'\W', '_', question[:30]).lower()
        document_id = f"doc_{number}_{sanitized_question}"

        # Format the document string
        chunk = '\n'.join([
            f'question:\n{question}\n',
            f'answer:\n{answer}\n',
        ])

        documents.append({
            'chunk': chunk,
            'data': {
                'number': number,
                'question': question,
                'answer': answer
            },
            'document_id': document_id,
        })

    print(f'Documents: {len(documents)}')

    return documents



def transformToAddTokensBySpacyNLP(documents: List[Dict], *args, **kwargs):
    """
    Template code for a transformer block to Lemmatize.
    """
    count = len(documents)
    print('Documents', count)

    nlp = spacy.load('en_core_web_sm')
    
    data = []

    for idx, document in enumerate(documents):
        document_id = document['document_id']
        if idx % 100 == 0:
            print(f'{idx + 1}/{count}')

        # Process the text chunk using spacy
        chunk = document['chunk']
        doc = nlp(chunk)
        tokens = [token.lemma_ for token in doc]

        data.append(
            dict(
                chunk=chunk,
                document_id=document_id,
                tokens=tokens,
                question=document['data']['question'],
                answer=document['data']['answer'],
            )
        )

    print('\nData', len(data))

    return data


def transformToAddEmbeddingBySpecy(documents: List[Dict], *args, **kwargs) ->List[Dict]:
    """
    Template code for a transformer block to create embeddings.
    """
    # Specify your transformation logic here
    count = len(documents)
    print('Documents', count)

    data = []

    for idx, document in enumerate(documents):
        document_id = document['document_id']
        if idx % 100 == 0:
            print(f'{idx + 1}/{count}')
        nlp = spacy.load('en_core_web_sm')
        tokens = document['tokens']
    
        # Combine tokens back into a single string of text used for embedding
        text = ' '.join(tokens)
        doc = nlp(text)
    
        # Average the word vectors in the doc to get a general embedding
        embedding = np.mean([token.vector for token in doc], axis=0).tolist()
    
        data.append(dict(
            chunk=document['chunk'],
            document_id=document['document_id'],
            question=document['question'],
            answer=document['answer'],
            embedding=embedding,
        ))

    return data


def transformToAddEmbeddingByST(documents: List[Dict], *args, **kwargs) ->List[Dict]:
    """
    Template code for a transformer block to create embeddings by Sentence Transformer.
    """
    # Specify your transformation logic here
    count = len(documents)
    print('Documents', count)

    model = SentenceTransformer("all-MiniLM-L6-v2")
    
    data = []

    for idx, document in enumerate(documents):
        embedding = model.encode(document['chunk'])
    
        data.append(dict(
            chunk=document['chunk'],
            document_id=document['document_id'],
            question=document['question'],
            answer=document['answer'],
            embedding=embedding,
        ))

    return data


def export_dataToIndex(documents: List[Dict[str, Union[Dict, List[int], str]]], *args, **kwargs):
    """
    Exports data to some source.
    
    """
    # Specify your data exporting logic here
    connection_string = kwargs.get('connection_string', 'http://localhost:9200')
    index_name = kwargs.get('index_name', 'documents')
    number_of_shards = kwargs.get('number_of_shards', 1)
    number_of_replicas = kwargs.get('number_of_replicas', 0)
    dimensions = kwargs.get('dimensions')

    if dimensions is None and len(documents) > 0:
        document = documents[0]
        dimensions = len(document.get('embedding'))
        print(f"Dimensions:{dimensions}")

    es_client = Elasticsearch(connection_string, request_timeout=60.0)

    print(f'Connecting to Elasticsearch at {connection_string}')

    index_settings = {
            "settings": {
                "number_of_shards": number_of_shards,
                "number_of_replicas": number_of_replicas,
            },
            "mappings": {
                "properties": {
                    "chunk": {"type": "text"},
                    "document_id": {"type": "text"},
                    "question": {"type": "text"},
                    "answer": {"type": "text"},
                    "embedding": {
                        "type": "dense_vector", 
                        "dims": dimensions,
                        "index": True,
                        "similarity": "cosine"
                    },
                }
            }
        }
    
    if es_client.indices.exists(index=index_name):
        es_client.indices.delete(index=index_name)
        print(f'Index {index_name} deleted')

    es_client.indices.create(index=index_name, body=index_settings)
    print('Index created with properties:')
    print(json.dumps(index_settings, indent=2))
    print('Embedding dimensions:', dimensions)

    count = len(documents)
    print(f'Indexing {count} documents to Elasticsearch index {index_name}')
    for idx, document in enumerate(documents):
        if idx % 2 == 0:
            print(f'Indexing.. {idx + 1}/{count}')

        if isinstance(document['embedding'], np.ndarray):
            document['embedding'] = document['embedding'].tolist()

        es_client.index(index=index_name, document=document)

    return [d['embedding'] for d in documents[:1]]

def is_elasticsearch_ready():
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
        return response.status_code == 200
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to Elasticsearch service: {e}")
        return False

def check(index_name, es_client):
    try:
        result = es_client.count(index=index_name)
        print(f"ES Checking = Document count in {index_name}: {result['count']}")
    except Exception as e:
        print(f"ES Checking = Error: {str(e)}")
def main():
    
    if not is_elasticsearch_ready():
        print("ElasticSearch instance not running. exiting..")
        sys.exit(1)

    es_client = Elasticsearch('http://localhost:9200',request_timeout=20.0)

    df = load_data()
    chunk_documents = transformToAddChunk(df)
    lemmatize_documents = transformToAddTokensBySpacyNLP(chunk_documents)
    
    embedding_documentsBySpecy = transformToAddEmbeddingBySpecy(lemmatize_documents)
    embedding_documentsByST = transformToAddEmbeddingByST(lemmatize_documents)
    
    export_dataToIndex(embedding_documentsByST,index_name="documents_st")
    export_dataToIndex(embedding_documentsBySpecy,index_name="documents_spacy")
    
    print("Index Created Successfully")

if __name__ == "__main__":
    main()    