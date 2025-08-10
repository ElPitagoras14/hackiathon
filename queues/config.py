from dotenv import find_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict


class GeneralSettings(BaseSettings):
    API_KEY: str
    REDIS_URL: str
    IN_DOCKER: bool = False

    IG_USERNAME: str
    IG_PASSWORD: str

    model_config = SettingsConfigDict(
        env_file=find_dotenv(filename=".env", usecwd=True),
        env_file_encoding="utf-8",
        extra="ignore",
    )


general_settings = GeneralSettings()
