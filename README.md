# Banking Core Withdrawal API

A FastAPI-based banking core withdrawal service with full observability, audit logging, and domain-driven design.

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

### Prerequisites
- Python 3.13+
- pip package manager

### Installation

```bash
# Clone the repository
git clone [here](https://github.com/tsotetsi/banking-withdrawal-fastapi.git)
cd banking-withdrawal-fastapi

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements/local.txt


### Running the Application
# Start the FastAPI server with auto-reload
uvicorn app.main:app --reload
```

### 📚 After Running Uvicorn

Once the server is running (typically at http://localhost:8000), you can access:

### 🔍 Interactive API Documentation

Swagger UI: http://localhost:8000/docs

Interactive API explorer with try-it-out functionality.

Full endpoint documentation with request/response schemas.

### 📖 Alternative Documentation

ReDoc: http://localhost:8000/redoc

Beautiful, responsive API documentation.

Better for reading and understanding API structure.

### 🏠 API Root & Health Check

Root Endpoint: http://localhost:8000/

Welcome message and API status

Health Check: http://localhost:8000/health


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

### 📡 API Usage

Withdrawal Request Example
```bash
curl -X POST "http://localhost:8000/api/v1/withdrawal" \
  -H "Content-Type: application/json" \
  -d '{
    "account_id": "1234567890",
    "amount": 100.50,
    "correlation_id": "req-12345"
  }'
Example Response
json
{
  "transaction_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "account_id": "1234567890",
  "amount": 100.50,
  "balance": 899.50,
  "correlation_id": "req-12345"
}
```

### 🐳 Docker Support (Coming Soon)

Dockerfile for containerized deployment

docker-compose for local development with databases.

### 📝 License

Apache 2.0 - See LICENSE file for details.

### 🤝 Contributing

Fork the repository.

Create a feature branch.

Add tests for new functionality.

Submit a pull request.