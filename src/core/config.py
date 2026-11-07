from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    qdrant_url: str | None = None
    qdrant_api_key: str | None = None

    embedding_model_name: str = "intfloat/multilingual-e5-small"
    embedding_dim: int = 384


settings = Settings()
