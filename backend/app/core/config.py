from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "EcoVision AI Backend"
    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_db: str = "ecovision"
    model_path: str = "./model/waste_classifier.keras"
    confidence_threshold: float = 0.45
    cors_origins: str = "http://localhost:5173"
    jwt_secret: str = "change-this-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    storage_backend: str = "local"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @property
    def cors_origins_list(self) -> list[str]:
        return [item.strip() for item in self.cors_origins.split(",") if item.strip()]

    @property
    def cloud_provider(self) -> str:
        if self.mongodb_uri.startswith("mongodb+srv://"):
            return "MongoDB Atlas (Free Tier)"
        return "Local MongoDB"


settings = Settings()
