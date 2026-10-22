"""Connection settings, read from environment variables.

The variable names and defaults match `compose.yaml`, so the app works with
the local database container without any extra configuration.
"""

import os
from dataclasses import dataclass
from functools import lru_cache

from sqlalchemy import URL


@dataclass(frozen=True)
class Settings:
    db_host: str
    db_port: int
    db_user: str
    db_password: str
    db_name: str

    @property
    def database_url(self) -> URL:
        return URL.create(
            drivername="postgresql+psycopg",
            username=self.db_user,
            password=self.db_password,
            host=self.db_host,
            port=self.db_port,
            database=self.db_name,
        )


@lru_cache
def get_settings() -> Settings:
    return Settings(
        db_host=os.environ.get("POSTGRES_HOST", "localhost"),
        db_port=int(os.environ.get("POSTGRES_PORT", "5432")),
        db_user=os.environ.get("POSTGRES_USER", "app"),
        db_password=os.environ.get("POSTGRES_PASSWORD", "app"),
        db_name=os.environ.get("POSTGRES_DB", "games"),
    )
