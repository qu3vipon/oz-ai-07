# configuration: 구성

from pydantic_settings import BaseSettings, SettingsConfigDict


# 프로젝트 내의 비밀키 값을 관리하는 클래스
class Settings(BaseSettings):
    openai_api_key: str

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
