build:
	docker-compose build --build-arg UNAME=$$(whoami) \
		--build-arg UID=$$(id -u) --build-arg GID=$$(id -g)
rebuild:
	docker rmi routes4life-api_api && docker-compose build \
		--build-arg UNAME=$$(whoami) --build-arg UID=$$(id -u) \
		--build-arg GID=$$(id -g)
run:
	docker-compose up -d
stop:
	docker-compose down
test:
	docker-compose run api python -m pytest && docker-compose down
#lint: