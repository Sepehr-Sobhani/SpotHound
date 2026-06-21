from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg2://spothound:spothound@localhost:5432/spothound"
    jwt_secret: str = "change-me-in-dev"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24

    telegram_bot_token: str | None = None
    headless: bool = True  # default for new targets; overridden per-target

    admin_username: str = "admin"
    admin_password: str = "admin"  # override via env in real use


settings = Settings()
