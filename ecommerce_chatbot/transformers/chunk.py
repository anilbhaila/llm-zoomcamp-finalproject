import pandas as pd
import re

if 'transformer' not in globals():
    from mage_ai.data_preparation.decorators import transformer
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test


@transformer
def transform(data: pd.DataFrame, *args, **kwargs):
    """
    Template code for a transformer block.

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


@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, 'The output is undefined'
