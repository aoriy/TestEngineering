from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    app_name: str = "TestEngineering"
    debug: bool = False

    database_url: str = "sqlite:///./data.db"

    cors_origins: list[str] = ["http://localhost:5173"]

    # AI self-heal (ADR-0005)
    deepseek_api_key: str = ""
    deepseek_base_url: str = "https://api.deepseek.com"
    deepseek_model: str = "deepseek-v4-pro"
    selfheal_mode: str = "suggest"  # auto / suggest / off

    # execution (ADR-0001)
    runs_dir: str = "runs"
    step_timeout_seconds: int = 60
    run_timeout_seconds: int = 1800
    selfheal_call_limit: int = 30


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
