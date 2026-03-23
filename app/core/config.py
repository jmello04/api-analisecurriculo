from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql://postgres:postgres@localhost:5432/resume_analyzer"
    anthropic_api_key: str
    analysis_model: str = "claude-opus-4-6"
    log_level: str = "INFO"
    max_upload_size_mb: int = 10

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
