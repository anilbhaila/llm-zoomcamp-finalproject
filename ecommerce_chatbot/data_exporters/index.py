import json

from typing import Dict, List, Union

import numpy as np
from elasticsearch import Elasticsearch, helpers


if 'data_exporter' not in globals():
    from mage_ai.data_preparation.decorators import data_exporter


@data_exporter
def export_data(documents: List[Dict[str, Union[Dict, List[int], str]]], *args, **kwargs):
    """
    Exports data to some source.

    Args:
        data: The output from the upstream parent block
        args: The output from any additional upstream blocks (if applicable)

    Output (optional):
        Optionally return any object and it'll be logged and
        displayed when inspecting the block run.
    """
    # Specify your data exporting logic here
    connection_string = kwargs.get('connection_string', 'http://elasticsearch:9200')
    index_name = kwargs.get('index_name', 'documents_spacy')
    number_of_shards = kwargs.get('number_of_shards', 1)
    number_of_replicas = kwargs.get('number_of_replicas', 0)
    dimensions = kwargs.get('dimensions')

    if dimensions is None and len(documents) > 0:
        document = documents[0]
        dimensions = len(document.get('embedding') or [])

    es_client = Elasticsearch(connection_string)

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
        
    # 1. Build actions generator/list for the bulk helper
    bulk_actions = []
    for document in documents:
        # Prevent NumPy array conversion crashes
        if isinstance(document['embedding'], np.ndarray):
            document['embedding'] = document['embedding'].tolist()
            
        action = {
            "_index": index_name,
            "_source": document
        }
        bulk_actions.append(action)
        
    # 2. Execute bulk insertion in a single optimized pipeline operation
    print("Sending batch payload to Elasticsearch...")
    success, errors = helpers.bulk(es_client, bulk_actions)
    print(f"Successfully indexed {success} documents.")
    
    if errors:
        print(f"Warning: Encounted errors during indexing: {errors}")
        
    # 3. Force index refresh so elements are immediately available for search
    es_client.indices.refresh(index=index_name)

    return [d['embedding'] for d in documents[:5]]



