# llm-zoomcamp-finalproject
Final Project for llm-zoomcamp-2026 course.

$pip install uv
$uv init
$uv sync

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
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_USER=user 
POSTGRES_PASSWORD=password 
POSTGRES_HOST=postgres 
OPENAI_API_KEY=your-key-here

GRAFANA_ADMIN_USER=admin@admin.com
GRAFANA_ADMIN_PASSWORD=admin

MAGE_TRIGGER_URL=Your-Pipleline-Trigger-url

Open the Mage UI, go to your pipeline, click the Triggers tab, find your API trigger, and copy the new Token/cURL string. Paste that new value into your .env file
example:http://127.0.0.1:6789/api/pipeline_schedules/1/pipeline_runs/4c11159a05a246939d631299f86f96b5

Note: this needs to be create everytime fresh docker image is build.

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
POSTGRES_VERSION=1700
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


Mage can be reachable at: http://localhost:6789
Username: admin@admin.com
Password: admin


Magicai added to docker-compose.yml file.

$docker compose up  (will run all services, mage, postgres, elastic search, grafana, streamlit)

Note:
I have created graphana dashboard manually and exported as code (json). I placed this json code into Git hub. This same JSON is used to recreate Dashboard in Grafana Automatically via Python Code.

After you create, Grafana Datasource and Dashboard from Python code, you need to click Save&Test in Grafana UI in Datasource to make it work.


To do experiment in elasticsearch, add elastic search library in uv

$uv add elasticsearch (caused version mis-match)
$uv add "elasticsearch>=8,<9"

$uv add spacy  (For embeddings)

import en_core_web_sm is not working in notebook.

$uv run python -m spacy download en_core_web_sm

Now we will be able to load package via spacy.load('en_core_web_sm')


$uv add matplotlib (For result evaluation)
$uv add seaborn

We will be commenting elasticsearch volume in docker-compose.yml because codespace is running out of space and elasticsearch docker was unable to start.
#volumes:
#  - es_data:/usr/share/elasticsearch/data

So, this will not save our embeddings into disk and will be erased everytime we restart elasticsearch docker.

ISSUE: mage is not detecting my pipeline.
$docker compose down -v
$docker compose build --no-cache
$docker compose up


Spacy Embedding is not good in embeddings

So, to use "sentense-transformers" add below code to pyproject.toml
[tool.uv.sources]
torch = { index = "pytorch-cpu" }

[[tool.uv.index]]
name = "pytorch-cpu"
url = "https://download.pytorch.org/whl/cpu"

And in terminal execute below command:
$uv add sentence-transformers

Error will show as below:
× No solution found when resolving dependencies for split (markers: python_full_version >= '3.14' and sys_platform
  │ == 'win32'):
  ╰─▶ Because only requests==2.28.1 is available and your project depends on requests>=2.34.2, we can conclude that
      your project's requirements are unsatisfiable.


To resolve this issue downgraded requests==2.28.1 in pyproject.toml


Codespace disk was very low, so elastic search indexing was stuck and throws error.
So, run below commands to clean some space:
$docker system prune -a --volumes --force
$uv cache clean

freed some space and indexing worked.
$df -h /workspaces  (To check the disk space of codespaces)

I only want to rebuild "steamlit" docker image.
$docker compose down streamlit
$docker compose up --build -d streamlit

Elasticsearch indexing is running very slow. Run below curl command to check health of elastic search
curl -s http://localhost:9200/_cluster/health?pretty

Returned:
{
  "cluster_name" : "docker-cluster",
  "status" : "red",
  "timed_out" : false,
  "number_of_nodes" : 1,
  "number_of_data_nodes" : 1,
  "active_primary_shards" : 0,
  "active_shards" : 0,
  "relocating_shards" : 0,
  "initializing_shards" : 0,
  "unassigned_shards" : 1,
  "unassigned_primary_shards" : 1,
  "delayed_unassigned_shards" : 0,
  "number_of_pending_tasks" : 0,
  "number_of_in_flight_fetch" : 0,
  "task_max_waiting_in_queue_millis" : 0,
  "active_shards_percent_as_number" : 0.0
}

Status: Red, that's why indexing is giving error.

To explain why elastic search is crashing
curl -s "http://localhost:9200/_cluster/allocation/explain?pretty"



To change the watermark in elastic search.
curl -X PUT "http://localhost:9200/_cluster/settings" -H 'Content-Type: application/json' -d'
{
  "persistent": {
    "cluster.routing.allocation.disk.watermark.low": "95%",
    "cluster.routing.allocation.disk.watermark.high": "98%",
    "cluster.routing.allocation.disk.watermark.flood_stage": "99%"
  }
}'


$docker ps --filter "name=elasticsearch"

$docker logs --tail 50 -f elasticsearch-1


Diagnose which index is Broken
curl -s "http://localhost:9200/_cat/shards?v&h=index,shard,prirep,state,unassigned.reason"

Returned:
index        shard prirep state      unassigned.reason
documents_st 0     p      UNASSIGNED INDEX_CREATED

$docker compose down elasticsearch
$docker volume rm $(docker volume ls -q | grep es_data)
$docker compose down -v (to stop containers and destroy any hidden anonymous storage blocks)
$docker compose up -d elasticsearch

Shorten directory path in terminal:
$export PS1="> "