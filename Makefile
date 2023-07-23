postgres-user = postgres
postgres-database = postgres


build-dev:
	-cp -n ./.env.template ./.env
	docker compose build --build-arg "ENV=DEV"

up-dev:
	docker compose run --rm web bash -c "alembic upgrade head"
	docker compose up

build-prod:
	docker compose -f docker-compose.yml -f docker-compose.prod.yml build --build-arg "ENV=PROD"

up-prod:
	docker compose -f docker-compose.yml -f docker-compose.prod.yml run --rm web bash -c "alembic upgrade head"
	docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d

makemigrations:
	docker compose run --rm web bash -c "alembic revision --autogenerate"

migrate:
	docker compose run --rm web bash -c "alembic upgrade head"

bash:
	docker compose exec web bash

db-bash:
	docker compose exec db bash

db-shell:
	docker compose exec db psql -U $(postgres-user)

test:
	docker compose run --rm web bash -c "python3 -m pytest -s $(location)"
