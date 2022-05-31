build:
	docker-compose -f docker-compose.yml build --build-arg UNAME=$$(whoami) \
		--build-arg UID=$$(id -u) --build-arg GID=$$(id -g) --progress=plain
rebuild:
	docker rmi routes4life-api_api && docker-compose build \
		--build-arg UNAME=$$(whoami) --build-arg UID=$$(id -u) \
		--build-arg GID=$$(id -g) --progress=plain
run:
	docker-compose -f docker-compose.yml up -d
run-local:
	docker-compose -f docker-compose-test.yml up -d;\
	docker exec --tty $$(docker-compose -f docker-compose-test.yml ps -q api) \
		python -m gunicorn --bind 0.0.0.0:8000 --workers 4 config.wsgi:application &
stop:
	docker-compose -f docker-compose.yml down
stop-local:
	docker-compose -f docker-compose-test.yml down
test:
	docker-compose -f docker-compose-test.yml run api python -m pytest;\
	docker-compose -f docker-compose-test.yml down
lint:
	pre-commit run --all-files
build-testimage:
	docker-compose -f docker-compose-test.yml build --build-arg UNAME=$$(whoami) \
		--build-arg UID=$$(id -u) --build-arg GID=$$(id -g)
migrate:
	docker exec --tty $$(docker-compose -f docker-compose.yml ps -q api) python manage.py migrate


# push actual versions to DockerHub
push-api:
	docker build \
		--build-arg UNAME=$$(whoami) \
		--build-arg UID=$$(id -u) \
		--build-arg GID=$$(id -g) \
		-t flawlesse/routes4life_api_local:latest .;\
	docker push flawlesse/routes4life_api_local:latest

push-db:
	docker build -f Dockerfile_db . -t flawlesse/routes4life_db_local:latest;\
	docker push flawlesse/routes4life_db_local:latest

# FOR MOBILE DEVS
run-local-server:
	docker-compose -f docker-compose-local.yml up -d
stop-local-server:
	docker-compose -f docker-compose-local.yml down
migrate-local:
	docker exec --tty $$(docker-compose -f docker-compose-local.yml ps -q api) python manage.py migrate
