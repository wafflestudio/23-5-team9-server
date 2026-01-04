from pydantic_settings import BaseSettings, SettingsConfigDict
from carrot.settings import SETTINGS


class AuthSettings(BaseSettings):
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    FRONTEND_URL: str

    ACCESS_TOKEN_SECRET: str
    REFRESH_TOKEN_SECRET: str
    SESSION_SECRET: str
    SHORT_SESSION_LIFESPAN: int = 15
    LONG_SESSION_LIFESPAN: int = 24 * 60

    model_config = SettingsConfigDict(
        case_sensitive=False, env_file=SETTINGS.env_file, extra="ignore"
    )


AUTH_SETTINGS = AuthSettings()
