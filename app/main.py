from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import init_db
from app.routers import (
    api_definitions,
    flows,
    health,
    page_templates,
    projects,
    record,
    requirements,
    runs,
    selfheal,
    shape_types,
    testcases,
    traceability,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title=settings.app_name, debug=settings.debug, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(projects.router, prefix="/api")
app.include_router(requirements.router, prefix="/api")
app.include_router(testcases.router, prefix="/api")
app.include_router(traceability.router, prefix="/api")
app.include_router(page_templates.router, prefix="/api")
app.include_router(flows.router, prefix="/api")
app.include_router(shape_types.router, prefix="/api")
app.include_router(runs.router, prefix="/api")
app.include_router(api_definitions.router, prefix="/api")
app.include_router(selfheal.router, prefix="/api")
app.include_router(record.router, prefix="/api")
