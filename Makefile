# Configurações principais
ENV_FILE = .env
include $(ENV_FILE)
export $(shell sed 's/=.*//' $(ENV_FILE))

SERVICE = fastapi_app

# Basic commands
up:
	docker compose up

down:
	docker compose down

restart:
	docker compose down && docker compose up

logs:
	docker compose logs -f $(SERVICE)

shell:
	docker exec -it ${SERVICE} ipython

# Alembic Migrations
migrate:
	docker compose exec $(SERVICE) alembic upgrade head

makemigrations:
	docker exec $(SERVICE) alembic revision --autogenerate -m "$(m)"

downgrade:
	docker compose exec $(SERVICE) alembic downgrade -1

show_migrations:
	docker compose exec $(SERVICE) alembic history

# Banco de dados para desenvolvimento/testes
create-test-db:
	docker compose exec $(SERVICE) python src/tests/test_db.py

reset-test-db:
	docker compose exec $(SERVICE) python src/tests/test_db.py

# Formatters / linters
format:
	docker compose exec $(SERVICE) black src/ tests/

lint:
	docker compose exec $(SERVICE) flake8 src/ tests/

isort:
	docker compose exec $(SERVICE) isort src/ tests/

# Tests
test:
	docker exec $(SERVICE) pytest -s -v

test-cov:
	docker exec $(SERVICE) pytest -v --cov=src tests/

# Help
help:
	@echo "Comandos disponíveis:"
	@echo "  up                - Sobe os containers"
	@echo "  down              - Derruba os containers"
	@echo "  restart           - Reinicia os containers"
	@echo "  logs              - Logs do serviço principal"
	@echo "  shell             - Abre bash no container backend"
	@echo "  migrate           - Executa as migrations do Alembic"
	@echo "  makemigrations m='msg' - Cria uma nova migration"
	@echo "  downgrade         - Volta uma migration"
	@echo "  show_migrations   - Lista o histórico de migrations"
	@echo "  create-test-db    - Cria banco de testes e aplica migrations"
	@echo "  reset-test-db     - Reseta banco de testes (drop + migrate)"
	@echo "  format            - Executa Black"
	@echo "  lint              - Executa Flake8"
	@echo "  isort             - Executa Isort"
	@echo "  test              - Executa testes"
	@echo "  test-cov          - Executa testes com cobertura"
