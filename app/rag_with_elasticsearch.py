import time
from dataclasses import dataclass, field
from datetime import datetime

from rag_helper import RAGBase

from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer

import spacy
import numpy as np


@dataclass
class LLMCallRecord:
    model: str
    prompt: str
    instructions: str
    answer: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    response_time: float
    cost: float
    timestamp: datetime = field(default_factory=datetime.now)


def calculate_cost(model, usage):
    cost = 0
    if "gpt-5.4-mini" in model:
        cost = (usage.input_tokens * 0.15 + usage.output_tokens * 0.60) / 1_000_000
    return cost


class RAGWithElasticSearch(RAGBase):
     
    def __init__(self, embedder, search_client, search_type, *args, **kwargs):
        super().__init__(index=None, **kwargs)
        self.last_call: LLMCallRecord = None
        self.embedder = embedder
        self.search_type = search_type
        self.search_client = search_client

    

    def llm(self, prompt):
        start_time = time.time()
        response = self._call_llm(prompt)
        response_time = time.time() - start_time
        self._log_response(prompt, response, response_time)
        return response.output_text

    def _call_llm(self, prompt):
        input_messages = [
            {"role": "developer", "content": self.instructions},
            {"role": "user", "content": prompt}
        ]
        response = self.llm_client.responses.create(
            model=self.model,
            input=input_messages
        )
        return response
    
    def get_vector(self,query):
        if(isinstance(self.embedder,SentenceTransformer)):
            return self.embedder.encode(query)

        doc = self.embedder(query)
        tokens = [token.lemma_ for token in doc]
        text = ' '.join(tokens)
        doc_lemmatized = self.embedder(text)
        vector = np.mean([token.vector for token in doc_lemmatized], axis=0).tolist()
        return vector

    def search(self, query, num_results=5):
        index_name="documents_specy"
        if(isinstance(self.embedder,SentenceTransformer)):
            index_name = "documents_st"

        if self.search_type == 'text':
            search_results = self._elastic_search_text(query,index_name)
        elif self.search_type == 'vector':
            search_results = self._elastic_search_knn(query,index_name)
        elif self.search_type == 'hybrid':
            search_results = self._elastic_search_hybrid(query,index_name)
        
        return search_results


    def _elastic_search_text(self, query, index_name, num_results=5):
        

        search_query = {
            "size": num_results,
            "query": {
                "bool": {
                    "must": {
                        "multi_match": {
                            "query": query,
                            "fields": ["question^3", "answer"],
                            "type": "best_fields",
                        }   
                    },
                }
            }
        }

        response = self.search_client.search(index=index_name, body=search_query)
        return [hit["_source"] for hit in response["hits"]["hits"]]

    def _elastic_search_knn(self,query,index_name, num_results=5):
        vector = self.get_vector(query)

        search_body = {
            "knn": {
                "field": "embedding",
                "query_vector": vector,
                "k": num_results,
                "num_candidates": 10000,
            },
            "size": num_results,
            "_source": ['document_id', 'question', 'answer'],
        }

        es_results = self.search_client.search(index=index_name, body=search_body)

        return [hit["_source"] for hit in es_results["hits"]["hits"]]

    def _elastic_search_hybrid(self,query,index_name, num_results=5):
        vector = self.get_vector(query)
    
        knn_query = {
            "field": "embedding",
            "query_vector": vector,
            "k": num_results,
            "num_candidates": 10000,
            "boost": 0.5,
        }

        keyword_query = {
            "bool": {
                "must": {
                    "multi_match": {
                        "query": query,
                        "fields": ["question^3", "answer"],
                        "type": "best_fields",
                        "boost": 0.5,
                    }   
                },
            }
        }

        es_results = self.search_client.search(
            index=index_name,
            query=keyword_query,
            knn=knn_query,
            size=num_results
        )

        return [hit["_source"] for hit in es_results["hits"]["hits"]]

    def _log_response(self, prompt, response, response_time):
        usage = response.usage
        cost = calculate_cost(self.model, usage)

        call_record = LLMCallRecord(
            model=self.model,
            prompt=prompt,
            instructions=self.instructions,
            answer=response.output_text,
            prompt_tokens=usage.input_tokens,
            completion_tokens=usage.output_tokens,
            total_tokens=usage.total_tokens,
            response_time=response_time,
            cost=cost,
        )
    
        print(call_record)
        self.last_call = call_record