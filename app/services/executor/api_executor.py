from app.services.executor.base import Executor, RunRequest


class ApiExecutor(Executor):
    key = "api"

    def generate_code(self, request: RunRequest) -> str:
        # Phase 3: render pytest from flow steps via Jinja2 templates.
        return ""

    def build_command(self, request: RunRequest, generated_dir: str) -> list[str]:
        return ["uv", "run", "pytest", generated_dir]


class UiExecutor(Executor):
    key = "ui"

    def generate_code(self, request: RunRequest) -> str:
        # Phase 3: render Playwright POM pytest from flow steps.
        return ""

    def build_command(self, request: RunRequest, generated_dir: str) -> list[str]:
        return ["uv", "run", "pytest", generated_dir]


class PerfExecutor(Executor):
    key = "perf"

    def generate_code(self, request: RunRequest) -> str:
        # Phase 4: render locustfile.py from ApiDefinition.
        return ""

    def build_command(self, request: RunRequest, generated_dir: str) -> list[str]:
        return [
            "uv",
            "run",
            "locust",
            "-f",
            generated_dir,
            "--headless",
        ]
