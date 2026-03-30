from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    google_api_key: str = "AIzaSyAKonDfT8tX47eLcQhNkZWy7_4k57RqoEA"
    db_name: str
    database_url: str = f"user=randenrms dbname={db_name} password=D@rkF@th3r! host= sslmode=disable" 

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
