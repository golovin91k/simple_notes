from pathlib import Path
import sys

from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
sys.path.append(str(BASE_DIR))


class Settings(BaseSettings):
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    DOMAIN: str
    BOT_PATH: str
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
            f'@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}')

    # @property
    # def get_webhook_url(self):
    #     return f'{self.SITE_URL}/simple_notes_bot/webhook'
    @property
    def get_webhook_url(self):
        return f'{self.DOMAIN}/{self.BOT_PATH}/webhook'


settings = Settings()
