import sys
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
sys.path.append(str(BASE_DIR))


class Settings(BaseSettings):
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    # DB_NAME: str
    # DB_HOST: str
    # DB_PORT: int
    # DB_USER: str
    # DB_PASSWORD: str
    SITE_URL: str
    BOT_TOKEN: str
    ADMIN_TELEGRAM_ID: int
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / 'infra' / '.env',
        extra='ignore')

    @property
    def get_db_url(self):
        return (
            f'postgresql+asyncpg://{self.POSTGRES_USER}:'
            f'{self.POSTGRES_PASSWORD}'
            f'@db:5432/{self.POSTGRES_DB}')

    @property
    def get_webhook_url(self):
        return f'{self.SITE_URL}/simple_notes_bot/webhook'


settings = Settings()
# print(BASE_DIR)
# print(settings.get_webhook_url)
