build:
	docker-compose build --build-arg UNAME=$$(whoami) --progress=plain\
		--build-arg UID=$$(id -u) --build-arg GID=$$(id -g)
rebuild:
	docker rmi routes4life-api_api && docker-compose build --progress=plain\
		--build-arg UNAME=$$(whoami) --build-arg UID=$$(id -u) \
		--build-arg GID=$$(id -g)
run:
	docker-compose up -d
stop:
	docker-compose down
test:
	docker-compose -f docker-compose-test.yml run api python -m pytest;\
	docker-compose -f docker-compose-test.yml down
lint:
	pre-commit run --all-files
build-testimage:
	docker-compose -f docker-compose-test.yml build --build-arg UNAME=$$(whoami) \
		--build-arg UID=$$(id -u) --build-arg GID=$$(id -g) 