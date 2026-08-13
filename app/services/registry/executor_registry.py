"""Executor registry (ADR-0002). Add implementations, don't edit core."""

from app.services.executor.api_executor import ApiExecutor, PerfExecutor, UiExecutor
from app.services.executor.base import Executor

_registry: dict[str, Executor] = {
    ApiExecutor.key: ApiExecutor(),
    UiExecutor.key: UiExecutor(),
    PerfExecutor.key: PerfExecutor(),
}


def register(executor: Executor) -> None:
    _registry[executor.key] = executor


def get(key: str) -> Executor:
    try:
        return _registry[key]
    except KeyError:
        raise KeyError(f"unknown executor: {key}") from None


def keys() -> list[str]:
    return list(_registry.keys())
