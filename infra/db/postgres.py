import os
from typing import Optional

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

# Import Base để có thể tạo tables
from infra.db.base import Base


load_dotenv()


def _normalize_asyncpg_url(url: str) -> str:
    if url.startswith("postgresql+asyncpg://"):
        return url
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+asyncpg://", 1)
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+asyncpg://", 1)
    return url


class PostgresConnection:
    _instance: Optional["PostgresConnection"] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PostgresConnection, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self) -> None:
        # Ưu tiên POSTGRES_URL, fallback từ các biến rời
        raw_url = os.getenv("POSTGRES_URL")
        if not raw_url:
            host = os.getenv("POSTGRES_HOST", "localhost")
            port = os.getenv("POSTGRES_PORT", "5432")
            user = os.getenv("POSTGRES_USER", "postgres")
            password = os.getenv("POSTGRES_PASSWORD", "")
            database = os.getenv("POSTGRES_DB", "postgres")
            auth = f"{user}:{password}@" if password else f"{user}@"
            raw_url = f"postgresql+asyncpg://{auth}{host}:{port}/{database}"

        url = _normalize_asyncpg_url(raw_url)

        self.engine: AsyncEngine = create_async_engine(
            url,
            echo=os.getenv("POSTGRES_ECHO", "false").lower() == "true",
            pool_size=int(os.getenv("POSTGRES_POOL_SIZE", "5")),
            max_overflow=int(os.getenv("POSTGRES_MAX_OVERFLOW", "10")),
            pool_pre_ping=True,
        )
        self.session_maker: async_sessionmaker[AsyncSession] = async_sessionmaker(
            self.engine, expire_on_commit=False
        )

    async def create_tables(self):
        """Tạo tất cả tables từ Base metadata"""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    def get_engine(self) -> AsyncEngine:
        return self.engine

    def get_sessionmaker(self) -> async_sessionmaker[AsyncSession]:
        return self.session_maker


# Singleton export cho dùng chung
postgres = PostgresConnection()
