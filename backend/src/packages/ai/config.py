from pydantic import BaseSettings, Field
from functools import lru_cache

class Settings(BaseSettings):
    OPENAI_API_KEY: str | None = Field(default=None, env="OPENAI_API_KEY")
    API_KEY: str | None = Field(default=None, env="API_KEY")
    CHROMA_PERSIST_DIR: str = "./chroma_persist"
    MODEL_NAME: str = "gpt-4o-mini"
    EMBEDDING_MODEL: str = "text-embedding-3-small"

    def openai_key(self) -> str:
        return self.OPENAI_API_KEY or self.API_KEY or ""
    class Config:
        env_file = ".env"

@lru_cache
def get_settings() -> Settings:
    return Settings()
