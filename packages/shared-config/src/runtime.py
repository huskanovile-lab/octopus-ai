from pydantic_settings import BaseSettings


class RuntimeSettings(BaseSettings):
    app_name: str = "octopus-ai"
    redis_url: str = "redis://localhost:6379/0"
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/octopus"
    autonomy_mode: str = "autonomous_paper_mode"


settings = RuntimeSettings()
