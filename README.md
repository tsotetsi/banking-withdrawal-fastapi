# Banking Core Withdrawal API

<div align="center">

  [![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
  [![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
  [![Pydantic](https://img.shields.io/badge/-Pydantic-464646?logo=Pydantic)](https://docs.pydantic.dev/latest/)
  [![Python](https://img.shields.io/badge/Python-3.13+-3776ab?logo=python&logoColor=white)](https://www.python.org/)
  [![PostgreSQL](https://img.shields.io/badge/PostgreSQL-17+-316192?style=flat&logo=postgresql&logoColor=white)](https://www.postgresql.org)
  [![Prometheus](https://img.shields.io/badge/prometheus-3.0.6-fab005?style=flat&logo=prometheus)](https://prometheus.io/docs/introduction/overview/)
  [![Grafana](https://img.shields.io/badge/grafana-12.2-fab005?style=flat&logo=grafana)](https://grafana.com/docs/)
  [![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

</div>

> A FastAPI-based banking core withdrawal service with full observability, audit logging, and domain-driven design approach.

## Features

- ✅ RESTful Withdrawal API with validation.
- ✅ Domain-Driven Design architecture.
- ✅ Request correlation and distributed tracing.
- ✅ Performance monitoring with latency logging.
- ✅ Structured logging for observability.
- ✅ Event-driven architecture.
- ✅ Comprehensive error handling.
- ✅ Unit and integration tests.

## 🚀 Getting Started

#### Prerequisites
- Python 3.13+
- Docker and Docker compose

#### Installation

```bash
# Clone the repository
git clone https://github.com/tsotetsi/banking-withdrawal-fastapi.git
cd banking-withdrawal-fastapi
```
### 🐳 Docker Support

Run the following commad to spin-off all system services.

See `.env.example` for env values that you need to setup.

```bash
docker compose up --build
```

### 📖 Alternative Documentation

- ReDoc: http://localhost:8000/redoc

- Beautiful, responsive API documentation.

- Better for reading and understanding API structure.


### 🧪 Testing
```bash
# Run all tests
pytest -v

# Run with coverage report
pytest --cov=app --cov-report=html

# Run specific test categories
pytest tests/unit/ -v
pytest tests/integration/ -v
```

### 🏗️ Architecture(DDD directory structure)
```text
app/
├── domain/           # Business logic layer
│   ├── models.py     # Domain models
│   ├── services.py   # Business services
│   └── exceptions.py # Domain exceptions
├── infrastructure/   # Technical implementation
│   ├── repository.py # Data persistence
│   ├── event_bus.py  # Event publishing
│   └── middleware/   # HTTP middlewares
├── schemas/          # API contracts
│   └── withdrawal.py # Request/response schemas
└── api/              # HTTP layer
    └── v1/           # API versioning
```
### 📡 API Usage

Withdrawal Request Example
```bash
curl -X POST "http://localhost:8000/api/v1/withdrawal"   -H "Content-Type: application/json"   -d '{
    "account_id": "1234567",
    "amount": 50.00,
    "correlation_id": "123e4567-e89b-12d3-a456-426614174001"
  }'
```

**Example Response**

```json
{
  "transaction_id":"f4f3128e-bdd7-4cda-bb6c-0e0cc885bc3d","account_id":"42a52f24-7359-4b31-8dac-b884bb4eb861","amount":"50.00","balance":"600.00","correlation_id":"123e4567-e89b-12d3-a456-426614174001"
}
```

## Access Grafana
- Go to: http://localhost:3000
Login: admin/admin

- Add Prometheus datasource: http://prometheus:9090

- Create dashboard or import the banking dashboard

- Available Metrics:
**http_requests_total** - Request count by endpoint and status
**http_request_duration_seconds** - Request latency
**withdrawal_requests_total** - Withdrawal success/failure rates
**withdrawal_amount** - Distribution of withdrawal amounts
**transaction_processing_seconds** - Transaction processing time

### 📝 License

MIT License - See LICENSE file for details.

### 🤝 Contributing

Fork the repository.

Create a feature branch.

Add tests for new functionality.

Submit a pull request.
