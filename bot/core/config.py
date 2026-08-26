from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str
    database_url_sync: str

    bot_token: str
    bot_username: str
    admin_bot_token: str
    admin_bot_username: str
    seller_bot_token: str
    seller_bot_username: str
    telegram_proxy_url: str | None = None
    miniapp_url: str
    admin_webapp_url: str
    analytics_url: str = "https://miramaxmpp.uz/analytics/"
    backend_url: str
    store_phone: str = "+998999929292"

    seed_factory_telegram_id: int
    seed_supplier_telegram_id: int
    seed_supplier_name: str
    superuser_telegram_id: int = 5008217282

    admin_web_login: str = "admin"
    admin_web_password: str


settings = Settings()
