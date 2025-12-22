# API de Cotação de Moedas — Desafio Técnico Backend

API desenvolvida em **Python + FastAPI** para retornar a melhor cotação de moeda (a mais barata) entre Dólar, Euro e Libra.

---

## 🎯 Objetivo do Desafio

Desenvolver uma aplicação com uma única rota que retorna a **cotação da melhor moeda para compra** no momento, sendo esta a mais barata entre as opções selecionadas (Dólar, Euro e Libra).

### Particularidades dos Serviços de Cotação

| Moeda     | Comportamento                                                                   |
| --------- | ------------------------------------------------------------------------------- |
| **Dólar** | Retorna o valor de forma imediata                                               |
| **Euro**  | Simula latência de rede (1s a 5s)                                               |
| **Libra** | Retorna via **webhook** — envia um token e a resposta é recebida em um callback |

### Nível de Dificuldade

| Nível      | Endpoints Consultados |
| ---------- | --------------------- |
| **Sênior** | Dólar, Euro, Libra    |
| **Pleno**  | Dólar, Euro           |
| **Júnior** | Dólar, Euro           |

> Esta implementação contempla o **nível Sênior** (todos os endpoints, incluindo Libra via webhook).

---

## 🏗️ Arquitetura da Solução

```
src/
├── api/v1/endpoints/   # Endpoints da API (rotas)
│   └── price.py        # Rota principal /best e webhook
├── core/               # Configurações e settings
├── schemas/quotation/  # Schemas Pydantic (validação)
├── services/quotation/ # Lógica de negócio (cotações)
├── tests/              # Testes unitários
└── main.py             # Entry point da aplicação
```

### Design Patterns Utilizados

- **Service Layer Pattern**: Lógica de negócio isolada em `QuotationService`
- **Dependency Injection**: Configuração via `QuotationServiceConfig`
- **Repository Pattern** (preparado): Estrutura pronta para persistência
- **Event-Driven**: Uso de `asyncio.Event` para aguardar webhooks

---

## 🚀 Tecnologias Utilizadas

- [FastAPI](https://fastapi.tiangolo.com/) — Web framework assíncrono
- [HTTPX](https://www.python-httpx.org/) — Cliente HTTP async
- [Pydantic](https://docs.pydantic.dev/) — Validação de dados
- [Docker](https://www.docker.com/) — Contêinerização
- [Pytest](https://pytest.org/) — Framework de testes
- [Loguru](https://github.com/Delgan/loguru) — Logging estruturado
- [Uvicorn](https://www.uvicorn.org/) — ASGI server

---

## ⚙️ Como Executar

### ✅ Pré-requisitos

- **Docker e Docker Compose** instalados

---

### 🚀 Executando com Docker (Recomendado)

```bash
# 1. Clone o repositório (branch backend_amigoz)
git clone -b backend_amigoz --single-branch https://github.com/Pissinatti-py/fastapi-boilerplate.git
cd fastapi-boilerplate

# 2. Crie o arquivo .env (ou copie o .env.example)
cp .env.example .env

# 3. Suba a aplicação junto com o serviço de cotações
docker-compose up --build
```

O `docker-compose` irá iniciar:

- **quotation_app** (porta 8000) — Nossa API
- **quotation_service** (porta 3000) — Serviço de cotações do desafio

#### ✅ Acesse:

| Recurso      | URL                                             |
| ------------ | ----------------------------------------------- |
| API Endpoint | http://localhost:8000/api/v1.0/quotation/best   |
| Swagger Docs | http://localhost:8000/docs                      |
| ReDoc        | http://localhost:8000/redoc                     |
| Health Check | http://localhost:8000/api/v1.0/quotation/health |

---

## 📡 Endpoints da API

### `GET /api/v1.0/quotation/best`

Retorna a melhor cotação entre as moedas disponíveis.

**Parâmetros Query:**

| Parâmetro       | Tipo | Default | Descrição                                |
| --------------- | ---- | ------- | ---------------------------------------- |
| `include_pound` | bool | `true`  | Incluir Libra na consulta (nível Sênior) |

**Exemplo de Requisição:**

```bash
# Nível Sênior (Dólar + Euro + Libra)
curl http://localhost:8000/api/v1.0/quotation/best

# Nível Pleno/Júnior (Dólar + Euro)
curl "http://localhost:8000/api/v1.0/quotation/best?include_pound=false"
```

**Exemplo de Resposta:**

```json
{
  "top_quotation": {
    "currency": "Dollar",
    "code": "USD",
    "value": 5.5
  },
  "all_quotation": [
    { "currency": "Dollar", "code": "USD", "value": 5.5 },
    { "currency": "EURO", "code": "EUR", "value": 6.25 },
    { "currency": "Libra Esterlina", "code": "GBP", "value": 7.15 }
  ],
  "response_time_ms": 1234.56
}
```

### `POST /api/v1.0/quotation/webhook/pound`

Endpoint de callback para receber a cotação da Libra via webhook.

> Este endpoint é chamado automaticamente pelo serviço de cotações.

---

## 🧪 Testes

### Estrutura de Testes

Os testes unitários estão localizados em `src/tests/` e cobrem:

- **Configuração do serviço** (`QuotationServiceConfig`)
- **Consulta de Dólar** (sucesso, erro HTTP, erro de conexão)
- **Consulta de Euro** (sucesso, erro HTTP, latência)
- **Recebimento de Webhook** (request_id conhecido/desconhecido)
- **Melhor cotação** (cenários variados)

### Executando os Testes

```bash
# Com Docker (recomendado)
docker exec quotation_app pytest -s -v

# Testes com cobertura
docker exec quotation_app pytest -v --cov=src tests/

# Usando Make
make test
make test-cov
```

### Casos de Teste Implementados

| Teste                                  | Descrição                                   |
| -------------------------------------- | ------------------------------------------- |
| `test_get_dollar_success`              | Cotação do dólar retornada com sucesso      |
| `test_get_dollar_http_error`           | Erro HTTP ao consultar dólar                |
| `test_get_euro_success`                | Cotação do euro retornada com sucesso       |
| `test_get_euro_http_error`             | Erro HTTP ao consultar euro                 |
| `test_receive_webhook_known_request`   | Webhook recebido para request_id válido     |
| `test_receive_webhook_unknown_request` | Webhook recebido para request_id inválido   |
| `test_get_best_quote_without_pound`    | Melhor cotação sem libra                    |
| `test_get_best_quote_euro_is_best`     | Euro como melhor cotação                    |
| `test_get_best_quote_with_pound`       | Melhor cotação incluindo libra              |
| `test_get_best_quote_all_fail`         | Tratamento quando todas as consultas falham |

---

## 🛠️ Comandos Úteis

```bash
# Ver todos os comandos disponíveis
make help

# Subir containers
make up

# Derrubar containers
make down

# Reiniciar containers
make restart

# Ver logs
make logs

# Executar testes
make test

# Executar testes com cobertura
make test-cov

# Formatar código
make format

# Linting
make lint
```

---

## 📁 Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto:

```env
# Aplicação
APP_NAME=Cotacao Moedas API
APP_VERSION=1.0.0
DEBUG=true

# Serviço de Cotações
COTACAO_SERVICE_URL=http://quotation-service:3000
COTACAO_TIMEOUT=10.0
COTACAO_LIBRA_WAIT_TIMEOUT=5.0
```

---

### Docker Compose

O arquivo `docker-compose.yml` já está configurado para subir:

- A aplicação na porta **8000**
- O serviço de cotações (`mostela/desafiocotacoes`) na porta **3000**

---

## 🛡️ Licença

Este projeto foi desenvolvido como parte de um desafio técnico.
