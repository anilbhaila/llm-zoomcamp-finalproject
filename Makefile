make run:
	uv run python app/assistant.py

dashboard:
	uv run streamlit run app/dashboard.py

chat:
	uv run streamlit run app/app.py

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
	uv run python app/db_init.py

query:
	uv run python app/db_query.py

live-data:
	uv run python app/generate_data.py