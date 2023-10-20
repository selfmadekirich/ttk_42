SHELL=/bin/bash
DOCKER_COMPOSE_FILE=docker-compose.yaml

.PHONY: start

start: ##запуск необходимых для модуля контейнеров  в Docker
	@echo "Module start containers [`pwd | xargs basename`], started"		
	docker compose --env-file ./.env  -f ./$(DOCKER_COMPOSE_FILE) up -d;	true;
	@echo "Completed OK"