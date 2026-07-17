"""Application configuration using Pydantic Settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Database settings
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_USER: str = "fatloss"
    DB_PASSWORD: str = "fatloss123"
    DB_NAME: str = "fatloss_pk"

    # JWT settings
    JWT_SECRET: str = "change-me"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_DAYS: int = 7

    # Open Food Facts API
    OFF_API_URL: str = "https://cn.openfoodfacts.org"


    # Email SMTP settings (QQ Mail)
    SMTP_HOST: str = "smtp.qq.com"
    SMTP_PORT: int = 465
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM_NAME: str = "减脂PK"
    VERIFICATION_CODE_EXPIRE_MINUTES: int = 5

    # WeChat Mini Program (for one-click wx login via code2session)
    WX_APPID: str = ""
    WX_SECRET: str = ""

    @property
    def DATABASE_URL(self) -> str:
        """Build the SQLAlchemy database URL for MySQL."""
        return (
            f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?charset=utf8mb4"
        )


settings = Settings()
