import uuid
import structlog

from starlette.middleware.base import BaseHTTPMiddleware


logger = structlog.get_logger()


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    """Request/response logging middleware."""

    async def dispatch(self, request, call_next):
        correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))

        log = logger.bind(
            correlation_id=correlation_id,
            method=request.method,
            url=str(request.url)
            )

        log.info("request_started")

        try:
            response = await call_next(request)
            response.headers["X-Correlation-ID"] = correlation_id
            log.info("request_completed", status_code=response.status_code)
        except Exception as e:
            log.error("request_error", error=str(e))
            raise
        return response
