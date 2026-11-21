from pydantic_settings import BaseSettings, SettingsConfigDict

class settings(BaseSettings):
    PROJECT_NAME: str
    DATABASE_URL: str
    SECRET_KEY: str

    model_config=SettingsConfigDict(env_file=".env")
settings=settings()