from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "sqlite:///./spend_tracker.db"
    jwt_secret: str = "dev-only-change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 24 * 7
    cookie_name: str = "spend_tracker_token"
    cookie_secure: bool = False
    demo_username: str = "demo"
    demo_password: str = "spendtracker"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
