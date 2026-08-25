"""
Conversion Architect API - FastAPI Application

Provides HTTP endpoints for the Framer plugin and other clients to access
GA4 analytics, conversion insights, and genome compilation services.
"""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from conversion_architect.api.config import get_settings
from conversion_architect.api.ga4_routes import router as ga4_router
from conversion_architect.api.services import GA4Service

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    logger.info(
        f"app.starting name={settings.app_name} env={settings.app_env} ga4={settings.ga4.enabled}"
    )
    
    # Initialize GA4 service
    app.state.ga4_service = GA4Service(
        property_id=settings.ga4.property_id,
        credentials_path=settings.ga4.credentials_path,
        project_id=settings.ga4.project_id,
        mcp_command=settings.ga4.mcp_command,
        cache_ttl=settings.ga4.cache_ttl_seconds,
    )
    await app.state.ga4_service.startup()
    
    logger.info("app.started")
    
    yield
    
    # Shutdown
    logger.info("app.shutdown")
    await app.state.ga4_service.shutdown()


def create_app() -> FastAPI:
    """Create FastAPI application."""
    app = FastAPI(
        title="Conversion Architect API",
        description="GA4 analytics proxy and conversion insights API",
        version="0.1.0",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )
    
    # CORS middleware - allow browser origins for Framer plugin
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.api.cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["*"],
    )
    
    # Include routers
    app.include_router(ga4_router)
    
    # Health endpoint
    @app.get("/health", tags=["Health"])
    async def health_check():
        return {
            "status": "healthy",
            "service": settings.app_name,
            "env": settings.app_env,
            "ga4_enabled": settings.ga4.enabled,
        }
    
    # Root
    @app.get("/", tags=["Root"])
    async def root():
        return {
            "service": "Conversion Architect API",
            "version": "0.1.0",
            "docs": "/docs",
            "health": "/health",
            "ga4": {
                "analytics": "/api/v1/ga4/analytics",
                "insights": "/api/v1/ga4/insights",
                "accounts": "/api/v1/ga4/accounts",
            },
        }
    
    # Global exception handler
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error(f"unhandled_exception error={exc} path={request.url.path}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error"},
        )
    
    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "conversion_architect.api.main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.app_debug,
    )