from fastapi import APIRouter

from app.api.routes import api_keys, auth, ingest, projects, traces

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth.router)
api_router.include_router(projects.router)
api_router.include_router(api_keys.router)
api_router.include_router(ingest.router)
api_router.include_router(traces.router)
