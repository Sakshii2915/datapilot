from typing import List, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # Project metadata
    PROJECT_NAME: str = "DataPilot - Natural Language to SQL Analytics Agent"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    ENVIRONMENT: str = "development"

    # OpenAI Configuration
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"

    # Database Configuration
    DATABASE_URL: str = "sqlite:///./datapilot.db"
    READONLY_DATABASE_URL: str = ""

    # Query Safety & Resource Limits
    MAX_RESULT_ROWS: int = 100
    QUERY_TIMEOUT_SECONDS: int = 10
    MAX_SQL_CORRECTION_ATTEMPTS: int = 3

    # CORS Configuration
    CORS_ORIGINS: Union[List[str], str] = ["http://localhost:5173", "http://localhost:3000", "*"]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            return [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, (list, tuple)):
            return list(v)
        return ["*"]

    @property
    def is_mock_llm(self) -> bool:
        """Determines if the LLM engine should operate in documented mock mode."""
        return not self.OPENAI_API_KEY or self.OPENAI_API_KEY.strip().lower() in ("mock", "none", "", "test")

    @property
    def effective_readonly_db_url(self) -> str:
        """Returns read-only DB url, falling back to DATABASE_URL if not explicitly configured."""
        if self.READONLY_DATABASE_URL and self.READONLY_DATABASE_URL.strip():
            return self.READONLY_DATABASE_URL.strip()
        return self.DATABASE_URL

settings = Settings()
