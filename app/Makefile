make run:
	uv run python assistant.py

dashboard:
	uv run streamlit run dashboard.py

chat:
	uv run streamlit run app.py

network:
	@docker network ls | grep -q "monitoring" || docker network create monitoring

postgres: network
	docker stop ecommerce_chatbot-pg
	docker rm ecommerce_chatbot-pg
	docker run -it \
    --name ecommerce_chatbot-pg \
	--network monitoring \
    -e POSTGRES_USER=user \
    -e POSTGRES_PASSWORD=password \
    -e POSTGRES_DB=ecommerce_chatbot \
    -v pgdata:/var/lib/postgresql/data \
    -p 5432:5432 \
    pgvector/pgvector:pg17

init-db:
	uv run python db_init.py

query:
	uv run python db_query.py

