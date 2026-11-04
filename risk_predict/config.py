from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    openai_api_key: str
    jwt_secret_key: str

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
