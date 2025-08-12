from dotenv import find_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

class CompanySettings(BaseSettings):
    # ya existentes
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXP_MIN: int
    REFRESH_TOKEN_EXP_DAY: int

    # nuevo: credenciales/modelo del LLM
    API_KEY: str  # ej: OpenAI key
    MODEL: str = "gpt-4o-mini"  # o el que uses

    model_config = SettingsConfigDict(
        env_file=find_dotenv(filename=".env", usecwd=True),
        env_file_encoding="utf-8",
        extra="ignore",
    )

company_settings = CompanySettings()

