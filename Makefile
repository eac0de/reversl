
ar:
	@read -p "Enter migration message: " m; \
	alembic revision --autogenerate -m "$$m"

auh:
	alembic upgrade head

run:
	uvicorn app.main:app --host 0.0.0.0 --port 8888 --reload

up:
	docker compose up --build
	
down:
	docker compose down

clear:
	docker system prune