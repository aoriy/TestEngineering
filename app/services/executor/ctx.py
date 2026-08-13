"""Controlled execution context for code hooks (ADR-0003).

Exposes only get_var/set_var/log/call_api/sleep/fail. No os/subprocess/open.
"""

import time
from typing import Any, Callable

from app.core.varlib import VariableStore


class Ctx:
    def __init__(
        self,
        store: VariableStore,
        log_fn: Callable[[str], None],
        call_api_fn: Callable[[int, dict], Any],
    ):
        self._store = store
        self._log = log_fn
        self._call_api = call_api_fn

    def get_var(self, name: str, default: Any = None) -> Any:
        return self._store.get(name, default)

    def set_var(self, name: str, value: Any, scope: str = "page") -> None:
        self._store.set(name, value, scope)

    def log(self, msg: Any) -> None:
        self._log(str(msg))

    def call_api(self, api_id: int, params: dict | None = None) -> Any:
        return self._call_api(api_id, params or {})

    def sleep(self, seconds: float) -> None:
        time.sleep(float(seconds))

    def fail(self, reason: str) -> None:
        raise AssertionError(str(reason))
