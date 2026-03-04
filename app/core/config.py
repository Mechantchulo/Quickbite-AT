from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_NAME: str = "QuickBite USSD"
    APP_ENV: str = "development"
    APP_DEBUG: bool = Field(default=True, alias="APP_DEBUG")

    DATABASE_URL: str

    # Africa's talking
    AT_USERNAME: str = "sandbox"
    AT_API_KEY: str = ""
    AT_SERVICE_CODE: str = "*384*6235#"
    AT_USSD_CALLBACK_URL: str | None = None
    AT_AUTH_TOKEN: str | None = None
    INTERNAL_API_KEY: str | None = None

    # Payhero
    PAYHERO_BASIC_AUTH: str = ""
    API_USERNAME: str | None = None
    API_PASSWORD: str | None = None
    CHANNEL_ID: int | None = None
    URL: str = "https://backend.payhero.co.ke/api/v2/payments"
    PROVIDER: str = "m-pesa"
    CALLBACK_URL: str = ""
    PAYHERO_CALLBACK_TOKEN: str | None = None
    AT_USSD_EVENT_CALLBACK_URL: str | None = None

    _ROOT_ENV = Path(__file__).resolve().parents[3] / ".env"
    _LOCAL_ENV = Path(__file__).resolve().parents[2] / ".env"

    model_config = SettingsConfigDict(
        env_file=(_ROOT_ENV, _LOCAL_ENV),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

settings = Settings()
