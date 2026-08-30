"""Liveness/readiness endpoint."""

from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
async def health() -> dict[str, str]:
    """Return a simple OK payload for load balancers and uptime checks."""
    return {"status": "ok"}
