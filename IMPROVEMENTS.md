## Simple Banking Withdrawal System - Architectural Improvements
#### Executive Summary
I have transformed a simple Spring Boot banking controller into a production-ready, domain-driven, event-driven microservice architecture using FastAPI and Python. The reason behind the choice is soly based on the fact that I'm currently using FastAPI and wanted to speed-up development. The improvements enhance scalability, maintainability, observability, and fault tolerance while preserving all original business logic. Note that, I went as far as creating the system to demostrate some of the requirements as per the assessment.

#### Core Business Functionality Preserved
- Account balance validation and sufficient funds checking.

- Atomic balance update operations.

- Event notification for successful withdrawals.

- Transaction integrity and consistency.

- Basic error handling for insufficient funds.

#### Architectural Improvements
##### 1. Domain-Driven Design Implementation
Before: Anemic(sqlalchemy ORM) Data Model.

```java
// Simple data container without behavior
public class WithdrawalEvent {
    private BigDecimal amount;
    private Long accountId;
    private String status;
    // Only getters, no business logic
}
```

After: Rich Domain Model with Behavior with minimal required information.

```python
@dataclass
class BankAccount:
    """Domain model encapsulating business rules."""
    id: str
    account_number: str
    balance: Decimal
    created_at: datetime
    updated_at: datetime
    
    def has_sufficient_funds(self, amount: Decimal) -> bool:
        """Business rule: Check if withdrawal is possible."""
        return self.balance >= amount
    
    def withdraw(self, amount: Decimal) -> Decimal:
        """Business operation: Perform withdrawal with validation"""
        if not self.has_sufficient_funds(amount):
            raise InsufficientFundsError("Insufficient funds.")
        self.balance -= amount
        self.updated_at = datetime.now(timezone.utc)
        return self.balance
```

#### 2. Layered Architecture
#### Separation of Concerns:

- **Domain Layer**: Business models, services, and exceptions.

- **Infrastructure Layer**: Database, event publishing, external services.

- **API Layer**: HTTP endpoints, validation, and serialization.

- **Benefits**: Testability, maintainability, and technology independence.

#### 3. Event-Driven Architecture
**Before**: The code was tightly coupled.

```java
// SNS client created in controller
// Event publishing mixed with business logic
PublishResponse publishResponse = snsClient.publish(publishRequest);
```

**After**: Decoupled Event Publishing.

```python
# Abstract event publisher interface
class EventPublisher:
    def publish(self, event: WithdrawalEvent) -> None:
        pass

# Multiple implementations
class LocalStackEventPublisher(EventPublisher):
    # AWS SNS via LocalStack for development
    pass

class InMemoryEventPublisher(EventPublisher):
    # Fallback for testing
    pass
```

#### 4. Database and Transaction Management

**Before**: There was race conditions.

```java
// Race condition between SELECT and UPDATE
String sql = "SELECT balance FROM accounts WHERE id = ?";
BigDecimal currentBalance = jdbcTemplate.queryForObject(sql, new Object[]{accountId}, BigDecimal.class);
// ... time gap ...
sql = "UPDATE accounts SET balance = balance - ? WHERE id = ?";
```

**After**: Added **Atomic** operations with ORM.

```python
# Repository pattern with proper transaction management
class PostgresRepository:
    @contextmanager
    def get_session(self):
        """Transactional scope with automatic rollback."""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except SQLAlchemyError:
            session.rollback()
            raise
```

#### 5. Enhanced Error Handling.

**Before**: String-based Responses, which can be difficult to test.

```java
return "Insufficient funds for withdrawal";
```

**After**: Added Structured Error Handling.

```python
# Domain-specific exceptions.
class InsufficientFundsError(Exception):
    """Business exception for insufficient funds."""

class AccountNotFoundError(Exception):
    """Business exception for missing accounts."""

# HTTP exception mapping
@app.exception_handler(InsufficientFundsError)
async def insufficient_funds_handler(request: Request, exc: InsufficientFundsError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": str(exc), "type": "insufficient_funds"}
    )
```

#### 6. Observability and Monitoring

**Added Capabilities**:

- **Request Correlation**: UUID tracking across services via middlewares.

- **Structured Logging**: JSON-formatted logs with context.

- **Performance Metrics**: Latency monitoring and threshold alerts.

- **Health Checks**: Container health monitoring endpoints.

- **Audit Trails**: Complete transaction history written to database.

**Implementation**:

```python
# Correlation ID middleware
class CorrelationIdMiddleware:
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, request: Request, call_next):
        correlation_id = request.headers.get('X-Correlation-ID', str(uuid.uuid4()))
        request.state.correlation_id = correlation_id
        response = await call_next(request)
        response.headers['X-Correlation-ID'] = correlation_id
        return response
```

#### 7. Containerization and DevOps.

Complete Docker Setup:

```yaml
services:
  postgres:    # PostgreSQL database with persistence
  api:         # FastAPI application with hot reload
  localstack:  # AWS SNS/SQS for event streaming
  prometheus:  # Metrics collection
  grafana:     # Monitoring dashboard
```

**Benefits**: Reproducible environments, easy onboarding, `CI\CD` can be done using `GihubActions`

#### 1. API Design and Validation

**Before**: Basic Parameter Validation.

```java
public String withdraw(@RequestParam("accountId") Long accountId, 
                       @RequestParam("amount") BigDecimal amount)
```

**After**: Comprehensive Schema Validation.

```python
class WithdrawalRequest(BaseModel):
    """Pydantic schema with validation"""
    account_id: str = Field(..., pattern=r'^\d{7,14}$')
    amount: Decimal = Field(..., gt=0)
    correlation_id: UUID = Field(...)
    
    @field_validator("amount")
    def validate_amount_precision(cls, value: Decimal) -> Decimal:
        """Round to 2 decimal places for currency"""
        return value.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
```

#### Technology Choices

- **FastAPI** over **Spring Boot** since I'm currently using it at the moment:
    Async/Await: Better for I/O-bound operations like banking APIs.

- **Type Safety**: Pydantic provides runtime type validation.

* **Documentation**: Automatic OpenAPI docs generation.

* **Performance**: Comparable to Go and Node.js implementation(s).

* **PostgreSQL** over Other Databases:
* **ACID Compliance**: Critical for financial transactions.

* **Reliability**: Proven in production banking systems.

* **JSON Support**: Flexible for storing transaction metadata.

* **LocalStack** over Cloud Services:
* **Development Speed**: Local AWS services for development.

* **Cost Efficiency**: No cloud costs during development.

* **Offline Capability**: Work without internet connection.

* **Production Readiness Features**
* **Health Checks**: /health endpoint for monitoring.

* Metrics: Prometheus metrics endpoint at /metrics

* Structured Logging: JSON logs for log aggregation systems.

* Containerization: Docker setup for consistent deployments.

* Database Migrations: Ready for Alembic migration system.

* Configuration Management: Environment-based configuration.

* Performance Considerations.
Connection Pooling: SQLAlchemy connection pool for database.

* Async Operations: Non-blocking I/O for better throughput.

* Caching Ready: Architecture prepared for Redis integration.

* Horizontal Scaling: Stateless API ready for load balancing.

* Future Enhancement Preparedness.
Microservices Ready: Event-driven architecture prepared for service splitting.

* Audit Trail: Complete transaction history for compliance.

* Monitoring: Built-in metrics and logging for observability.

* Deployment: Containerized setup for Kubernetes readiness.

## Conclusion

The transformed implementation maintains all original business functionality while providing a scalable, maintainable, and production-ready architecture. The system is prepared for high-volume banking operations with proper error handling, observability, and operational excellence features.

The improvements demonstrate modern software engineering practices while respecting the domain complexity of banking operations.

