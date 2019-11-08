# Type `make` or `make help` to list available targets

# Concise introduction to GNU Make:
# https://swcarpentry.github.io/make-novice/reference.html

# The `-` in front of a command makes its exit status being ignored. Normally, a
# non-zero exit status stops the build.

# Taken from https://www.client9.com/self-documenting-makefiles/
help: ## Print this help
	@awk -F ':|##' '/^[^\t].+?:.*?##/ {\
		printf "\033[36m%-30s\033[0m %s\n", $$1, $$NF \
	}' $(MAKEFILE_LIST)
.PHONY: help
.DEFAULT_GOAL := help

clean-pyc: ## Remove all `pyc`-files
	find . -name '*.pyc' -exec rm --force {} \ 
.PHONY: clean-pyc

setup: ## Create network `scope-net` and volume `fuseki-db-data`
	-docker network create scope-net
	-docker volume create fuseki-db-data
.PHONY: setup

teardown: ## Remove network `scope-net` and volume `fuseki-db-data`
	-docker network rm scope-net
	-docker volume rm fuseki-db-data
.PHONY: teardown

clear-data: ## Re-create volume `fuseki-db-data` whereby all data is cleared
	-docker stop fuseki-db
	-docker rm -v fuseki-db
	-docker volume rm fuseki-db-data
	-docker volume create fuseki-db-data
.PHONY: clear-data

clear-data-restart:clear-data up

.PHONY: clear-data-restart

build: ## Re-build images
	docker-compose build
.PHONY: build

up: setup build ## Set-up network and volume, re-build images and start services
	docker-compose up \
		-d \
		--remove-orphans
.PHONY: up

up-prod: setup build ## Set-up network and volume, re-build images and start services with production settings
	docker-compose \
		--file docker-compose.yml \
		--file docker-compose.production.yml \
		up \
		-d \
		--remove-orphans
.PHONY: up-prod

logs: ## Display log output from services
	docker-compose logs \
		--follow
.PHONY: logs

restart: ## Restart services
	docker-compose restart
.PHONY: restart

down: ## Stop services
	docker-compose down \
		--remove-orphans
.PHONY: down

exec: ## Run the command ${COMMAND} within the running container of the service ${SERVICE}, for example, `make SERVICE=fuseki-db COMMAND=ls exec`
	docker-compose exec ${SERVICE} ${COMMAND}
.PHONY: exec

shell: COMMAND = ash
shell: exec ## Drop into Alpine Linux's default shell, that is, BusyBox's implementation of the Almquist shell, in the working directory `/app` within the running container of the service ${SERVICE}, for example, `make SERVICE=fuseki-db shell`
.PHONY: shell

run: ## Run the one-time command ${COMMAND} in a fresh container for the service ${SERVICE}, for example, `make SERVICE=fuseki-db COMMAND=ls run`
	docker-compose run ${SERVICE} ${COMMAND}
.PHONY: run

play: COMMAND = ash
play: run ## Drop into the Almquist shell in the working directory `/app` within a fresh container for the service ${SERVICE}, for example, `make SERVICE=fuseki-db play`
.PHONY: play

remove: ## Stop services, remove their images and non-external volumes
	docker-compose down \
		--rmi all \
		--volumes \
		--remove-orphans
.PHONY: remove

prune: ## Remove all stopped containers, all networks not used by at least one container, all dangling images, all build cache
	docker system prune --force
.PHONY: prune

listn: ## List networks
	docker network ls
.PHONY: listn

listi: ## List images
	docker images
.PHONY: listi

listc: ## List containers
	docker ps -a
.PHONY: listc

list: listn listi listc ## List networks, images, and containers
.PHONY: list

inspectn: ## Inspect network `scope-net`
	docker network inspect scope-net
.PHONY: inspectn

inspectv: ## Inspect volume `fuseki-db-data`
	docker volume inspect fuseki-db-data
.PHONY: inspectv

inspect: inspectn inspectv ## Inspect network `scope-net` and volume `fuseki-db-data`
.PHONY: inspect
