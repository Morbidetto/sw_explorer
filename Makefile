tests:
	docker-compose run --rm django pytest
	docker-compose stop

migrate:
	docker-compose run --rm django python manage.py migrate
	docker-compose stop

makemigrations:
	docker-compose run --rm django python manage.py makemigrations
	docker-compose stop

stop:
	docker-compose stop

start:
	docker-compose up -d django