"""FastAPI application bootstrap for the HappyRobot carrier sales backend."""

from __future__ import annotations

# Load environment variables FIRST, before any internal module imports
from dotenv import load_dotenv

load_dotenv()

import os
import secrets

from fastapi import Depends, FastAPI, HTTPException, Request, Security, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader

from router.vetting import router as vetting_router
from router.matching import router as matching_router
from router.negotiation import router as negotiation_router
from router.call_logs import router as call_logs_router

API_KEY_HEADER_NAME = "X-API-KEY"
api_key_header = APIKeyHeader(name=API_KEY_HEADER_NAME, auto_error=False)


def verify_api_key(
    request: Request,
    api_key: str | None = Security(api_key_header),
) -> None:
    """Validate the inbound API key for all operational routes."""
    if request.url.path == "/":
        return

    expected_api_key = os.getenv("API_KEY", "").strip()
    provided_api_key = (api_key or "").strip()

    if (
        not expected_api_key
        or not provided_api_key
        or not secrets.compare_digest(provided_api_key, expected_api_key)
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API Key",
        )


app = FastAPI(
    title="HappyRobot Inbound Carrier Sales Agent",
    description="Stateless decision engine and tool provider for inbound carrier sales automation.",
    version="0.1.0",
    dependencies=[Depends(verify_api_key)],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register operational routers with API Key protection via app-level dependency
app.include_router(vetting_router)
app.include_router(matching_router)
app.include_router(negotiation_router)
app.include_router(call_logs_router)


@app.get("/")
def health_check() -> dict[str, str]:
    """Return a simple health-check payload for uptime monitoring."""
    return {
        "status": "online",
        "project": "HappyRobot Inbound Carrier Sales Agent PoC",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
