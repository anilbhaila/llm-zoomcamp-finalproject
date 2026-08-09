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

# Monitoring

Add below dependency:
$uv add streamlit

Add below Postgres configs in .env file:
POSTGRES_DB=ecommerce_chatbot 
POSTGRES_USER=user 
POSTGRES_PASSWORD=password 
POSTGRES_HOST=postgres 
OPENAI_API_KEY=your-key-here

Run below docker command to start postgres:
$docker run -it \
    --name ecommerce_chatbot-pg \
    -e POSTGRES_USER=user \
    -e POSTGRES_PASSWORD=password \
    -e POSTGRES_DB=ecommerce_chatbot \
    -v pgdata:/var/lib/postgresql/data \
    -p 5432:5432 \
    pgvector/pgvector:pg17

Created a Make file and added below frequently used commands:
make run:
	uv run python scripts/assistant.py

init-db:
	uv run python scripts/db_init.py


Steps to run the Ecommerce Chatbot application:
# Add .env file in the root folder. And add below code:
POSTGRES_USER=user
POSTGRES_PASSWORD=password
POSTGRES_DB=ecommerce_chatbot
OPENAI_API_KEY=Your-OpenAI-API-Key

Execute Below docker command to run postgres, grafana and Ecommerce Chatbot Streamlit app.
$docker compose up

$make init-db  (to initialize postgres database)

Streamlit Application can be reachable at: http://localhost:8501/
Grafana can be rechable at: http://127.0.0.1:3000/

After you successfully run grafana enter below credentials:
username: admin
password: admin

Then add Postgres Datasource:
Click Connections => Add new Connection

Host URL: postgres:5432
Database name: ecommerce_chatbot

Username:user
Password:password

TLS/SSL Mode: disable

Then click: Save & test

Now inside app/ folder, there is graphana-dashboard.json, import this json file into graphana to load the dashboard.

Near Search bar, click + button => Import dashboard => Upload dashboard JSON file.

That's it.

Dashboard will be blank with no data. 
So, run below command to generate synthetic data:

$make live-data (to generate synthetic data for live monitoring in Grafana Dashboard)


Run Elastic Search:
docker run -it --name elasticsearch \
  -p 9200:9200 \
  -p 9300:9300 \
  -e "discovery.type=single-node" \
  -e "xpack.security.enabled=false" \
  -e "ES_JAVA_OPTS=-Xms1g -Xmx1g" \
  docker.elastic.co/elasticsearch/elasticsearch:8.17.0


Run Magicai 
docker run -it --name mage \
-e REQUIRE_USER_AUTHENTICATION=0 \
-p 6789:6789 \
-v $(pwd):/home/src \
mageai/mageai:latest \
mage start ecommarce_chatbot

Username: admin@admin.com
Password: admin


Magicai added to docker-compose.yml file.

$docker compose up  (will run all services, mage, postgres, elastic search, grafana, streamlit)
