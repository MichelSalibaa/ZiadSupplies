import os
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Settings:
    """
    Application configuration loaded from environment variables.

    SMTP_* values should point to the mail server used for verification emails.
    EMAIL_FROM is the address customers see in their inbox.
    BASE_URL is used to build verification links (defaults to http://localhost:8000).
    """

    db_path: str = os.getenv("ZIAD_DB_PATH", os.path.join("data", "ziad_store.sqlite3"))
    smtp_host: Optional[str] = os.getenv("SMTP_HOST")
    smtp_port: int = int(os.getenv("SMTP_PORT", "587"))
    smtp_username: Optional[str] = os.getenv("SMTP_USERNAME")
    smtp_password: Optional[str] = os.getenv("SMTP_PASSWORD")
    email_from: Optional[str] = os.getenv("EMAIL_FROM")
    base_url: str = os.getenv("BASE_URL", "http://localhost:8000")
    email_use_tls: bool = os.getenv("SMTP_USE_TLS", "true").lower() != "false"


settings = Settings()
