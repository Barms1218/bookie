from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    google_api_key: str = "AIzaSyAKonDfT8tX47eLcQhNkZWy7_4k57RqoEA"
    database_url: str = 'user=randenrms dbname=bookie password=D@rkF@th3r! host=/var/run/postgresql sslmode=disable' 

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
