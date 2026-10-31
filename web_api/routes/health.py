"""Health and version routes."""

from fastapi import APIRouter
from repairforge import __version__
from web_api.schemas import HealthResponse

router = APIRouter(prefix="/api", tags=["health"])


@router.get("/health", response_model=HealthResponse)
def get_health() -> HealthResponse:
    """Return health status and API version."""
    return HealthResponse(
        status="ok",
        version=__version__,
        app_name="Forge Command",
        project="RepairForge AI",
    )

