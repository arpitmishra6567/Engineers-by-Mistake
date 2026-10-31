"""
FastAPI application for Forge Command (RepairForge AI).
"""

from __future__ import annotations

import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from repairforge import __version__
from web_api.routes import dashboard, evaluations, health, models, repairs, repositories, skills

app = FastAPI(
    title="Forge Command API",
    description="Web API integration layer for RepairForge AI automated code repair harness.",
    version=__version__,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS configuration allowing frontend development servers, Vercel deployments, and custom domains
allowed_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

env_cors = os.environ.get("CORS_ORIGINS", "")
if env_cors:
    for o in env_cors.split(","):
        cleaned = o.strip()
        if cleaned and cleaned not in allowed_origins:
            allowed_origins.append(cleaned)

allow_all_cors = os.environ.get("CORS_ALLOW_ALL", "false").lower() in ("true", "1", "yes")

# Regex to automatically accept any Vercel preview or production deployment domain
vercel_regex = os.environ.get("CORS_ORIGIN_REGEX", r"^https://.*\.vercel\.app$")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if allow_all_cors else allowed_origins,
    allow_origin_regex=None if allow_all_cors else vercel_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register route modules
app.include_router(health.router)
app.include_router(dashboard.router)
app.include_router(repairs.router)
app.include_router(evaluations.router)
app.include_router(repositories.router)
app.include_router(models.router)
app.include_router(skills.router)

# Health alias at root level for platform monitoring
@app.get("/health", tags=["health"], include_in_schema=False)
def get_root_health():
    """Root health alias for platform health checkers."""
    return health.get_health()


# Mount frontend production build if present, otherwise provide root API status
dist_dir = Path("frontend/dist")
if dist_dir.exists() and dist_dir.is_dir():
    app.mount("/", StaticFiles(directory=str(dist_dir), html=True), name="frontend")
else:
    @app.get("/", tags=["root"], include_in_schema=False)
    def get_api_root():
        """Root API status when frontend is deployed independently on Vercel."""
        return {
            "app_name": "Forge Command API",
            "project": "RepairForge AI",
            "version": __version__,
            "status": "online",
            "docs_url": "/docs",
            "health_url": "/api/health",
            "platform": "Railway Ready",
        }


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "0.0.0.0")
    uvicorn.run("web_api.main:app", host=host, port=port, reload=False)

