"""Code-hook safety guard (ADR-0003).

User Python in shape before_code/after_code is validated by AST import
whitelist and executed with a restricted globals namespace (only whitelisted
modules + a controlled `ctx`). Dangerous builtins are blocked.
"""

import ast
import builtins
import importlib

ALLOWED_IMPORTS = {
    "requests",
    "json",
    "re",
    "jsonpath_ng",
    "jsonpath_ng.ext",
    "datetime",
    "random",
    "decimal",
    "hashlib",
}

FORBIDDEN_BUILTINS = {
    "__import__",
    "eval",
    "exec",
    "compile",
    "open",
    "input",
    "memoryview",
    "globals",
    "locals",
    "vars",
    "dir",
    "getattr",
    "setattr",
    "delattr",
    "breakpoint",
    "exit",
    "quit",
}

# safe builtins exposed to hooks
_SAFE_BUILTINS = {
    name: getattr(builtins, name)
    for name in dir(builtins)
    if name not in FORBIDDEN_BUILTINS
}


class SecurityError(RuntimeError):
    pass


def validate_code(code: str) -> list[str]:
    """Return a list of violations (empty means safe)."""
    violations: list[str] = []
    try:
        tree = ast.parse(code)
    except SyntaxError as exc:
        return [f"syntax error: {exc.msg} at line {exc.lineno}"]

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.split(".")[0] not in ALLOWED_IMPORTS:
                    violations.append(f"import '{alias.name}' is not allowed")
        elif isinstance(node, ast.ImportFrom):
            root = (node.module or "").split(".")[0]
            if root not in ALLOWED_IMPORTS:
                violations.append(f"from '{node.module}' import is not allowed")
        elif isinstance(node, ast.Call):
            name = _call_name(node.func)
            if name in FORBIDDEN_BUILTINS:
                violations.append(f"'{name}()' is forbidden")

    return violations


def _call_name(node: ast.expr) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return None


def build_globals(ctx: object) -> dict:
    """Build the restricted globals namespace for a hook."""
    namespace: dict = {"__builtins__": _SAFE_BUILTINS, "ctx": ctx}
    for mod in sorted(ALLOWED_IMPORTS):
        try:
            namespace[mod.replace(".", "_")] = importlib.import_module(mod)
        except ImportError:
            continue
    # also expose common top-level modules by their simple name
    for simple in (
        "requests",
        "json",
        "re",
        "datetime",
        "random",
        "decimal",
        "hashlib",
    ):
        try:
            namespace[simple] = importlib.import_module(simple)
        except ImportError:
            continue
    return namespace


def run_hook(code: str, ctx: object) -> None:
    """Validate and execute a code hook with the given ctx."""
    if not code or not code.strip():
        return
    violations = validate_code(code)
    if violations:
        raise SecurityError("; ".join(violations))
    exec(compile(code, "<shape_hook>", "exec"), build_globals(ctx), {})
