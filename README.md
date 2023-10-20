# netizen2
WIP second version of Netizen, a FastAPI app that aims to recreate the backend for a simple social-network website. Uses SQLAlchemy for database access. Containerized with Docker and secured with JWT.
Inspired by hexagonal and clean architecture, altered to fit my preferences.

## Tech stack
* FastAPI `0.103.0`
* SQLAlchemy `2.0.22`
* Alembic `1.12.0`
* PostgreSQL `15.3`
* Docker
* Celery

## Functionality
SwaggerUI docs available at `localhost:8000/api/v1/docs`
### Users:
* Implemented authentication using JWT.
* Users can register, login, view their profile.
* After registration, an email is sent to the user with account activation link.

## Setup
1. Clone repository:
`$ git clone https://github.com/amadeuszklimaszewski/netizen2.git`
2. Run in root directory:
`$ make build-dev`
3. Provide `JWT_SECRET_KEY` in .env file
4. Run template: `$ make up-dev`


## Migrations
Declare new tables in `./src/infrastructure/database/tables/` directory. They will be automatically detected on creation of migration files.
Run `$ make makemigrations` to create migrations file.
Run `$ make migrate` to apply migration files in database.


## Tests
`$ make test`


## Makefile
`Makefile` contains useful command aliases
