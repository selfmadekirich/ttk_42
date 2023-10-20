SHELL=/bin/bash
DOCKER_COMPOSE_FILE=docker-compose.yaml
.PHONY: start

start: ##запуск необходимых для модуля контейнеров  в Docker
	@echo "Module start containers [`pwd | xargs basename`], started"
	@. ./db.sh
	@docker compose --env-file ./.env  -f ./$(DOCKER_COMPOSE_FILE) up -d;	true;
	@echo "Completed OK"

delete: ##запуск необходимых для модуля контейнеров  в Docker
	@echo "Module delete containers [`pwd | xargs basename`], started"
	@docker rm -f ttk_20_db
	@docker volume rm -f ttk_42_pg_data