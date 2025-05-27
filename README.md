# 🚀 FastAPI Boilerplate — Async + PostgreSQL + Alembic + Docker

Este projeto é um **boilerplate profissional** para desenvolvimento de APIs utilizando:

- ✅ **FastAPI** (Assíncrono e Performático)
- ✅ **SQLAlchemy Async**
- ✅ **PostgreSQL**
- ✅ **Alembic** (migrations automáticas)
- ✅ **Docker e Docker Compose**

Foi criado para ser a base sólida de qualquer projeto backend que precise de uma API robusta, escalável e moderna.

---

## 🎯 Propósito

- 🔥 Servir como ponto de partida para **futuros projetos**.
- 📦 Entregar uma arquitetura limpa, desacoplada e escalável.
- 🚀 Permitir execução de **migrações automáticas no startup** da aplicação.
- 🔧 Fornecer suporte a ambientes locais e produção com facilidade (Docker Ready).
- ...

---

## 🏗️ Estrutura do Projeto

src/
├── api/ # Endpoints da API (Rotas)
├── core/ # Configurações, segurança, settings
├── db/ # Sessão, base, handler de migrations
├── migrations/ # Arquivos do Alembic (controle de schema)
├── models/ # ORM Models (SQLAlchemy)
├── main.py # Entry point da aplicação (FastAPI instance)

---

## 🚀 Tecnologias Utilizadas

- [FastAPI](https://fastapi.tiangolo.com/) — Web framework moderno e assíncrono
- [SQLAlchemy Async](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html) — ORM assíncrono robusto
- [Alembic](https://alembic.sqlalchemy.org/) — Migrations para SQLAlchemy
- [PostgreSQL](https://www.postgresql.org/) — Banco de dados relacional
- [Docker](https://www.docker.com/) — Contêinerização
- [Loguru](https://github.com/Delgan/loguru) — Logging estruturado e elegante
- [Uvicorn](https://www.uvicorn.org/) — ASGI server

---

## ⚙️ Como Executar Localmente

### ✅ Pré-requisitos

- Docker e Docker Compose instalados
  **ou**
- Python 3.12+ com ambiente virtual

---

### 🚀 Executando com Docker (Recomendado)

```bash
# 1. Clone o repositório
git clone https://github.com/seu-usuario/seu-projeto.git
cd seu-projeto

# 2. Suba a aplicação
docker-compose up --build
```

#### ✅ Acesse:

API: http://localhost:8000

Documentação Swagger: http://localhost:8000/docs

Documentação Redoc: http://localhost:8000/redoc

---

## ⚙️ Executando sem Docker (modo local)

## 1. Crie o ambiente virtual

```bash
$ python -m venv .venv

$ source .venv/bin/activate # No Windows: .venv\Scripts\activate
```

## 2. Instale as dependências

pip install -r requirements.txt

## 3. Crie um arquivo .env (veja .env.example)

## 4. Rode as migrações manualmente (opcional, pois rodam no startup)

```bash
$ alembic upgrade head
```

## 5. Inicie o servidor

```bash
$ uvicorn src.main:app --reload
```

---

## 🚩 Próximos Passos / Roadmap

- 🔄 Implementar autenticação JWT

- 🔐 Middlewares de autorização e segurança (CORS, Headers, etc.)

- 🛠️ Logging estruturado (JSON para produção)

- 🩺 Healthcheck e readiness probes

- 📜 Documentação automática da API (Swagger/OpenAPI)

- ✅ Integração contínua (CI/CD) com GitHub Actions ou GitLab CI

- ☸️ Deploy em ambientes Kubernetes (com Helm Charts)

- 🚀 Suporte para Redis e Celery (Background Tasks e Filas)

- 📊 Observabilidade: Prometheus + Grafana

- 🔥 Suporte para testes de carga (Locust ou k6)

---

## 📌 Features Planejadas

✅ Banco de dados assíncrono com SQLAlchemy 2.0+

✅ Pipeline de migrations Alembic na inicialização

✅ Estrutura de testes isolada com banco separado

✅ Arquitetura limpa e escalável

🔜 Suporte para Background Tasks assíncronas

🔜 Integração WebSockets opcional

🔜 Rate Limiting com Redis

🔜 API versionada (v1, v2...)

---

### 🛠️ Comandos Úteis

```bash
$ make help
```

## 🧪 Rodar testes com cobertura

```bash
$ make tests
```

## 🤝 Contribuindo

Pull requests são bem-vindos! Para mudanças importantes, por favor abra uma issue primeiro para discutir o que você gostaria de alterar.

## 🛡️ Licença

Este projeto está licenciado sob a licença MIT.
