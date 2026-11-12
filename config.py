from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "ManhwaForge AI"
    environment: str = "development"
    database_url: str = "sqlite:///./manhwaforge.db"
    openai_api_key: str = ""
    openai_text_model: str = "gpt-4.1"
    upload_dir: str = "./storage/uploads"
    max_upload_mb: int = 30
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
