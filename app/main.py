from datetime import datetime
from fastapi import FastAPI

from app.infrastructure.middleware import CorrelationIdMiddleware, LatencyMiddleware
from app.infrastructure.logging import setup_logging
from app.api.v1 import withdrawal


setup_logging()

tags_metadata = [ # for API documentation.
    {
        "name": "withdrawals",
        "description": "Operations related to account withdrawals.",
    }
]

app = FastAPI(
    title="Banking Core Withdrawal API Service.",
    description="Simulation of a banking core withdrawal API service.",
    version="1.0.0",
    openapi_tags=tags_metadata,
    date=datetime.now().isoformat(),
    contact={
    "name": "Thapelo Tsotetsi",
    "email": "support@tsotetsi.com",
    "url": "https://tsotetsi.com/contact"
    },
    license_info={
    "name": "Apache 2.0",
    "url": "https://www.apache.org/licenses/LICENSE-2.0.html"
    }
)

app.add_middleware(CorrelationIdMiddleware)
app.add_middleware(LatencyMiddleware)

app.include_router(
    withdrawal.router,
    prefix="/api/v1",
)

@app.get("/")
async def root():
    """Root endpoint to verify service is running."""
    return {
        "message": "Welcome to the Banking Core Withdrawal API Service!",
        "status": "Running",
        "version": "1.0.0",
        "since": datetime.now().isoformat()
    }
