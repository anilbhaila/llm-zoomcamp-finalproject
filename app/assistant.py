import sys

from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

from ingest import load_faq_data, build_index
from metrics import RAGWithMetrics
from db_save import save_conversation

def create_assistant():
    load_dotenv()

    documents = load_faq_data()
    index = build_index(documents)

    return RAGWithMetrics(
        index=index,
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