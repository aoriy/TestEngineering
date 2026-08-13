"""Parse `playwright codegen --target=python` output into recorded actions."""

import re
from dataclasses import dataclass


@dataclass
class RecordedAction:
    action: str  # click / input / select
    locator_type: str  # data-testid / text / css / xpath
    locator_value: str
    value: str = ""


_LOCATOR_RE = re.compile(r"^page\.([a-zA-Z_]+)\((.*)\)\.([a-zA-Z_]+)\((.*)\)$")

_SKIP_PREFIXES = (
    "#",
    "from ",
    "import ",
    "def ",
    "page.goto",
    "expect(",
    "browser",
    "context",
    "with ",
    "async ",
    "page.wait",
    "page.pause",
)


def _unquote(s: str) -> str:
    s = s.strip()
    if len(s) >= 2 and s[0] in "\"'" and s[-1] in "\"'":
        return s[1:-1]
    return s


def _parse_locator(method: str, args: str) -> tuple[str, str]:
    if method == "locator":
        val = _unquote(args)
        if val.startswith("xpath="):
            return "xpath", val[len("xpath=") :]
        if val.startswith("//") or val.startswith("("):
            return "xpath", val
        return "css", val
    if method == "get_by_test_id":
        return "data-testid", _unquote(args)
    if method == "get_by_text":
        return "text", _unquote(args)
    if method == "get_by_placeholder":
        return "css", f'[placeholder="{_unquote(args)}"]'
    if method == "get_by_label":
        return "css", _unquote(args)
    if method == "get_by_role":
        m = re.search(r"name=[\"'](.+?)[\"']", args)
        if m:
            return "text", m.group(1)
        role = _unquote(args.split(",")[0])
        return "css", f'[role="{role}"]'
    return "text", _unquote(args)


def _map_action(action: str, action_args: str) -> tuple[str | None, str]:
    if action in ("click", "check", "uncheck", "dblclick", "tap"):
        return "click", ""
    if action in ("fill", "type"):
        return "input", _unquote(action_args)
    if action == "press":
        return "input", _unquote(action_args)
    if action == "select_option":
        return "select", _unquote(action_args)
    return None, ""


def parse_recorded_code(code: str) -> list[RecordedAction]:
    actions: list[RecordedAction] = []
    for raw in code.splitlines():
        line = raw.strip()
        if not line or line.startswith(_SKIP_PREFIXES):
            continue
        m = _LOCATOR_RE.match(line)
        if not m:
            continue
        method, args, action_name, action_args = m.groups()
        locator_type, locator_value = _parse_locator(method, args)
        action, value = _map_action(action_name, action_args)
        if action is None or not locator_value:
            continue
        actions.append(
            RecordedAction(
                action=action,
                locator_type=locator_type,
                locator_value=locator_value,
                value=value,
            )
        )
    return actions
