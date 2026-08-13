from fastapi import APIRouter

from app.services.registry import executor_registry

router = APIRouter()


@router.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "app": "TestEngineering",
        "executors": executor_registry.keys(),
    }
