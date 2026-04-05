"""
app/config.py — Carrega e valida variáveis de ambiente.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Banco de dados
    DB_HOST:     str = "localhost"
    DB_PORT:     int = 3306
    DB_USER:     str = "root"
    DB_PASSWORD: str = ""
    DB_NAME:     str = "auto_pecas"

    # Ollama
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL:    str = "llama3.2"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def db_uri(self) -> str:
        return (
            f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
            f"?charset=utf8mb4"
        )


settings = Settings()
