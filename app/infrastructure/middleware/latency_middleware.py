import structlog
import time

from fastapi import Request
from starlette.types import ASGIApp, Scope, Receive, Send


logger = structlog.get_logger()


class LatencyMiddleware:
    """Middleware to log request latency and performance metrics."""
    def __init__(self, app: ASGIApp, warn_threshold_ms: int = 1000, critical_threshold_ms: int = 3000):
        self.app = app
        self.warn_threshold = warn_threshold_ms
        self.critical_threshold = critical_threshold_ms

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            # Skip non-HTTP requests (like WebSocket).
            await self.app(scope, receive, send)
            return

        start_time = time.time()
        
        # Custom send function to capture response status.
        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                # Store status code when response starts.
                nonlocal status_code
                status_code = message["status"]
            await send(message)
        
        status_code = 200  # Default status code if not set.
        
        try:
            await self.app(scope, receive, send_wrapper)
        finally:
            duration = time.time() - start_time
            duration_ms = round(duration * 1000, 2)
            
            request = Request(scope, receive)
            path = scope.get("path", "unknown")
            method = scope.get("method", "unknown")
            
            correlation_id = getattr(request.state, 'correlation_id', 'unknown')
            
            # Log with appropriate level based on threshold.
            if duration_ms > self.critical_threshold:
                log_level = logger.error
                level = "CRITICAL"
            elif duration_ms > self.warn_threshold:
                log_level = logger.warning
                level = "WARN"
            else:
                log_level = logger.info
                level = "INFO"
            
            log_level(
                "Request latency",
                extra={
                    "correlation_id": correlation_id,
                    "method": method,
                    "path": path,
                    "duration_ms": duration_ms,
                    "status_code": status_code,
                    "level": level,
                    "type": "performance"
                }
            )
