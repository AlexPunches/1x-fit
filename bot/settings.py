import pathlib

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Bot configuration
    base_path: pathlib.Path = pathlib.Path(__file__).parent.absolute()

    bot_token: str = Field(..., description="Telegram bot token from BotFather")
    admin_id: str | None = Field(None, description="Admin user ID for administrative functions")

    # Notification times (in HH:MM format)
    weight_notification_time: str = Field("09:40", description="Time for weight notifications in HH:MM format")
    activity_notification_time: str = Field("22:01", description="Time for activity notifications in HH:MM format")

    # Database configuration
    database_path: pathlib.Path = base_path / "../data/database.db"

    # Charts configuration
    charts_dir: pathlib.Path = base_path / "../charts/"

    # Webhook configuration
    webhook_url: str | None = Field(None, description="Webhook URL for the bot")

    # Server configuration
    host: str = Field("0.0.0.0", description="Host for the web server")  # noqa:S104
    port: int = Field(8000, description="Port for the web server")

    # Application environment
    app_env: str = Field("production", description="Application environment (development or production)")

    # Logging configuration
    log_min_level: str = Field("INFO", description="Minimum logging level (DEBUG, INFO, WARNING, ERROR)")

    class Config:
        env_file = ".env"
        case_sensitive = False


# Create a global instance of settings
settings = Settings()
