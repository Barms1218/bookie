from pydantic_settings import BaseSettings, SettingsConfigDict
import os
from dotenv import load_dotenv

class Settings(BaseSettings):
    load_dotenv()

    google_api_key = os.getenv("API_KEY")
    database_url = os.getenv("DB_URL")

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
