"""Application settings loaded from environment variables."""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration for the Mindicator MCP server."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    db_path: Path = Path("mumbai_mindicator.sqlite")
    sql_row_limit: int = 100
    sql_timeout_ms: int = 5000
    log_level: str = "INFO"
    service_name: str = "mindicator-mcp"
    service_version: str = "0.1.0"
    host: str = "127.0.0.1"
    port: int = 8000


settings = Settings()
