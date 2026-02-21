"""
NitiLens Enterprise SaaS Platform - FastAPI Application

Multi-tenant compliance platform with:
- Multi-policy support
- Real-time alerts
- ERP/CRM connectors
- Multi-language processing
- RBAC authentication
- Production monitoring

Run with:
    uvicorn app.main:app --reload --port 8000

API docs: http://localhost:8000/docs
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from app.api.policies import router as policies_router
from app.api.datasets import router as datasets_router
from app.api.compliance import router as compliance_router
from app.api.reviews import router as reviews_router
from app.api.auth import router as auth_router
from app.api.connectors import router as connectors_router
from app.api.monitoring import router as monitoring_router
from app.api.remediation import router as remediation_router
from app.api.risk import router as risk_router
from app.api.policy_impact import router as policy_impact_router
from app.api.dashboard import router as dashboard_router
from app.api.subscription import router as subscription_router
from app.core.scheduler import start_scheduler, stop_scheduler

app = FastAPI(
    title="NitiLens Enterprise — AI Compliance SaaS Platform",
    description=(
        "Enterprise-grade multi-tenant compliance platform with:\n"
        "- Multi-policy support with versioning\n"
        "- Real-time violation alerts (Email, Slack, WebSocket)\n"
        "- ERP/CRM data connectors (PostgreSQL, MySQL, MongoDB, REST API, CSV)\n"
        "- Multi-language policy processing\n"
        "- Role-based access control\n"
        "- Production monitoring and metrics\n"
        "- Scalable architecture for millions of records"
    ),
    version="2.0.0",
    contact={"name": "NitiLens Team", "url": "https://github.com/GDG-Cloud-New-Delhi/hackfest-2.0"},
    license_info={"name": "MIT"},
)

# CORS configuration
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins + ["http://127.0.0.1:5173", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routers
app.include_router(auth_router)
app.include_router(policies_router)
app.include_router(datasets_router)
app.include_router(compliance_router)
app.include_router(reviews_router)
app.include_router(connectors_router)
app.include_router(monitoring_router)
app.include_router(remediation_router)
app.include_router(risk_router)
app.include_router(policy_impact_router)
app.include_router(dashboard_router)
app.include_router(subscription_router)


@app.on_event("startup")
async def on_startup():
    """Initialize services on startup"""
    start_scheduler()
    print("🚀 NitiLens Enterprise Platform started")
    print(f"📊 Environment: {os.getenv('ENVIRONMENT', 'development')}")
    print(f"📚 API Documentation: http://localhost:8000/docs")


@app.on_event("shutdown")
async def on_shutdown():
    """Cleanup on shutdown"""
    stop_scheduler()
    print("👋 NitiLens Enterprise Platform stopped")


@app.get("/", tags=["Health"])
def root():
    return {
        "service": "NitiLens Enterprise Compliance Platform",
        "version": "2.0.0",
        "status": "operational",
        "features": [
            "Multi-policy support",
            "Real-time alerts",
            "ERP/CRM connectors",
            "Multi-language processing",
            "RBAC authentication",
            "Production monitoring",
            "Automated remediation",
            "Policy impact analysis",
            "Predictive risk detection"
        ],
        "docs": "/docs",
        "health": "/health",
        "metrics": "/metrics"
    }


@app.get("/api", tags=["Health"])
def api_root():
    return {
        "endpoints": {
            "auth": "/api/auth",
            "policies": "/api/policies",
            "datasets": "/api/datasets",
            "compliance": "/api/compliance",
            "reviews": "/api/reviews",
            "connectors": "/api/connectors",
            "remediation": "/api/remediation",
            "risk": "/api/risk",
            "policy_impact": "/api/policy-impact",
            "health": "/health",
            "metrics": "/metrics",
            "stats": "/api/stats"
        }
    }
