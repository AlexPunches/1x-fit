
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Bot configuration
    bot_token: str = Field(..., alias="BOT_TOKEN", description="Telegram bot token from BotFather")
    admin_id: str | None = Field(None, alias="ADMIN_ID", description="Admin user ID for administrative functions")

    # Notification times (in HH:MM format)
    weight_notification_time: str = Field("22:40", alias="WEIGHT_NOTIFICATION_TIME", description="Time for weight notifications in HH:MM format")
    activity_notification_time: str = Field("22:42", alias="ACTIVITY_NOTIFICATION_TIME", description="Time for activity notifications in HH:MM format")

    # Database configuration
    database_path: str = Field("../data/database.db", alias="DATABASE_PATH", description="Path to SQLite database file")

    # Charts configuration
    charts_dir: str = Field("../charts/", alias="CHARTS_DIR", description="Directory to store generated charts")

    # Webhook configuration
    webhook_url: str | None = Field(None, alias="WEBHOOK_URL", description="Webhook URL for the bot")

    # Server configuration
    host: str = Field("0.0.0.0", alias="HOST", description="Host for the web server")
    port: int = Field(8000, alias="PORT", description="Port for the web server")

    # Application environment
    app_env: str = Field("production", alias="APP_ENV", description="Application environment (development or production)")

    # Logging configuration
    log_min_level: str = Field("INFO", alias="LOG_MIN_LEVEL", description="Minimum logging level (DEBUG, INFO, WARNING, ERROR)")

    class Config:
        env_file = ".env"
        case_sensitive = True


# Create a global instance of settings
settings = Settings()
