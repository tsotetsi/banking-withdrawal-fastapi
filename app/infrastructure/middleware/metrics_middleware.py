import time

from prometheus_client import Counter, Histogram


# Define metrics.
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP Requests',
    ['method', 'endpoint', 'status_code']
)

REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency in seconds',
    ['method', 'endpoint']
)

class MetricsMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope['type'] != 'http':
            await self.app(scope, receive, send)
            return

        start_time = time.time()
        method = scope['method']
        path = scope['path']
        
        # Create a custom send function to capture status code
        async def send_wrapper(message):
            if message['type'] == 'http.response.start':
                status_code = message['status']
                REQUEST_COUNT.labels(method=method, endpoint=path, status_code=status_code).inc()
                
                duration = time.time() - start_time
                REQUEST_LATENCY.labels(method=method, endpoint=path).observe(duration)
            
            await send(message)
        
        await self.app(scope, receive, send_wrapper)
