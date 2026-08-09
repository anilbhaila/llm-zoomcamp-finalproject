import pandas as pd
import requests

from pathlib import Path

if 'data_loader' not in globals():
    from mage_ai.data_preparation.decorators import data_loader
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test

url = "https://raw.githubusercontent.com/anilbhaila/llm-zoomcamp-finalproject/refs/heads/main/data/Ecommerce_FAQ_Chatbot_dataset.json"
limit_rows = None



@data_loader
def load_data(*args, **kwargs):
    """
    Extract data from URL. 
    
    """
    
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
    


@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, 'The output is undefined'