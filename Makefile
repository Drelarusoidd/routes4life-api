build:
	docker-compose build
rebuild:
	docker rmi routes4life-api_api && docker-compose build
run:
	docker-compose up
stop:
	docker-compose down
test:
	docker-compose run api pytest && docker-compose down
#lint: