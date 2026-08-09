from typing import Dict, List

import numpy as np
import spacy

if 'transformer' not in globals():
    from mage_ai.data_preparation.decorators import transformer
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test


@transformer
def transform(documents: List[Dict], *args, **kwargs) ->List[Dict]:
    """
    Template code for a transformer block.

    Add more parameters to this function if this block has multiple parent blocks.
    There should be one parameter for each output variable from each parent block.

    Args:
        data: The output from the upstream parent block
        args: The output from any additional upstream blocks (if applicable)

    Returns:
        Anything (e.g. data frame, dictionary, array, int, str, etc.)
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


@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, 'The output is undefined'
