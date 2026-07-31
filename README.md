# llm-zoomcamp-finalproject
Final Project for llm-zoomcamp-2026 course.

$pip install uv
$uv init

Libraries needed
$uv add minsearch python-dotenv toyaikit openai requests sqlitesearch toyaikit jupyter

Added .env file
OPENAI_API_KEY=Your_api_key

Added data folder to store the dataset downloaded from kaggle

Added notebook.ipynb to experiment with data.

Let's assume we have Large Data Set which consumes lots of time to perform indexing.
So, instead of makeing user wait while the system is started, we split out the indexing of data into seperate process and persist into data base. So, that the index is ready for User's query.

Thus, we added, persistant_rag_ingest.ipynb to ingest the data and index it.

Then, we added, persistant_rag.ipynb to accept user query, and execute our rag to get answer from llm.


