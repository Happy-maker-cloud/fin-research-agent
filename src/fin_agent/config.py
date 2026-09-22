from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    market_api_key: str = Field(default="")
    request_timeout: float = Field(default=5.0, gt=0)
    max_concurrency: int = Field(default=3, ge=1, le=20)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
