tests:
	docker-compose run --rm django pytest

migrate:
	docker-compose run --rm django sh -c "sleep 10 && python manage.py migrate"

makemigrations:
	docker-compose run --rm django python manage.py makemigrations

stop:
	docker-compose stop

start:
	docker-compose up -d django
