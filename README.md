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

Created and agent that will search and retry search feeding its previous results until valid answer is found. If answer is not found, it will not try to answer by itself rather response it could not find the answer.


Vector Search
You need to add below code to pyproject.toml to force uv to download only required libs for sentence-transformers. 

[tool.uv.sources]
torch = { index = "pytorch-cpu" }

[[tool.uv.index]]
name = "pytorch-cpu"
url = "https://download.pytorch.org/whl/cpu"

$uv add sentence-transformers

For vector_search_pgvector.ipynb, we need to run postgres database in docker.
$docker run -it \
    --name pgvector \
    -e POSTGRES_USER=user \
    -e POSTGRES_PASSWORD=pswd \
    -e POSTGRES_DB=faq \
    -v pgvector_data:/var/lib/postgresql/data \
    -p 5432:5432 \
    pgvector/pgvector:pg17

And to connect postgres frmo python we need pyscopg library.
$uv add psycopg[binary]

You will below error:
× No solution found when resolving dependencies for split (markers: python_full_version >= '3.14' and sys_platform ==
  │ 'win32'):
  ╰─▶ Because only requests==2.28.1 is available and your project depends on requests>=2.34.2, we can conclude that your
      project's requirements are unsatisfiable.

So, you need to change the version of requests=2.28.1 in pyproject.toml

Then run below command again:
$uv add psycopg[binary]