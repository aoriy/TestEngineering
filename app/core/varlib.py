"""Simplified `{{var}}` substitution engine (ADR-0004).

Variables are *values*, not templates. We do a plain regex substitution so that
variable content containing `{{` / `{%` / any template syntax is treated as
literal data and never evaluated. Jinja2 is reserved for code-gen templates only.
"""

import re
from dataclasses import dataclass, field

_VAR_RE = re.compile(r"\{\{\s*([a-zA-Z_][a-zA-Z0-9_.]*)\s*\}\}")


@dataclass
class VariableStore:
    """Four-scope variable container (global -> flow -> page -> local)."""

    global_vars: dict = field(default_factory=dict)
    flow_vars: dict = field(default_factory=dict)
    page_vars: dict = field(default_factory=dict)
    local_vars: dict = field(default_factory=dict)

    def get(self, name: str, default=None):
        for scope in (
            self.local_vars,
            self.page_vars,
            self.flow_vars,
            self.global_vars,
        ):
            if name in scope:
                return scope[name]
        return default

    def set(self, name: str, value, scope: str = "page") -> None:
        target = {
            "global": self.global_vars,
            "flow": self.flow_vars,
            "page": self.page_vars,
            "local": self.local_vars,
        }.get(scope)
        if target is None:
            raise ValueError(f"unknown scope: {scope}")
        target[name] = value

    def reset_page(self) -> None:
        self.page_vars.clear()

    def reset_flow(self) -> None:
        self.flow_vars.clear()
        self.page_vars.clear()

    def as_dict(self) -> dict:
        merged = {}
        for scope in (self.global_vars, self.flow_vars, self.page_vars, self.local_vars):
            merged.update(scope)
        return merged


def substitute(template: str, store: VariableStore) -> str:
    """Replace all `{{var}}` occurrences with values from the store.

    Unknown variables are left untouched (safer than raising) so that literal
    text accidentally matching the pattern is preserved.
    """

    def repl(match: re.Match) -> str:
        name = match.group(1)
        value = store.get(name, None)
        if value is None:
            return match.group(0)
        return str(value)

    return _VAR_RE.sub(repl, template)
