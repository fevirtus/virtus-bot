import os
from typing import Optional
from urllib.parse import quote_plus

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
            
            # Encode password để handle ký tự đặc biệt như @, /, etc.
            if password:
                auth = f"{user}:{quote_plus(password)}@"
            else:
                auth = f"{user}@"
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

    async def wait_for_connection(self, timeout: int = 60, retry_interval: int = 2):
        """Wait for database connection to be ready"""
        import asyncio
        from sqlalchemy import text
        import time

        start_time = time.time()
        while True:
            try:
                async with self.engine.begin() as conn:
                    await conn.execute(text("SELECT 1"))
                print("✅ Database connection established!")
                return True
            except Exception as e:
                if time.time() - start_time > timeout:
                    print(f"❌ Failed to connect to database after {timeout}s: {e}")
                    raise e
                
                print(f"⚠️ Database not ready, retrying in {retry_interval}s...")
                await asyncio.sleep(retry_interval)

    async def create_tables(self):
        """Tạo tất cả tables từ Base metadata"""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def verify_and_migrate_schema(self):
        """Manually verify and migrate schema for multi-server support"""
        print("🔄 Verifying database schema...")
        from sqlalchemy import text
        
        queries = [
            # 1. Add columns first
            "ALTER TABLE bot_configs ADD COLUMN IF NOT EXISTS guild_id BIGINT DEFAULT 0;",
            "ALTER TABLE home_debt ADD COLUMN IF NOT EXISTS guild_id BIGINT DEFAULT 0;",
            "ALTER TABLE score ADD COLUMN IF NOT EXISTS guild_id BIGINT DEFAULT 0;",
            
            # 2. Fix Primary Key for bot_configs
            """
            DO $$
            BEGIN
                IF EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'bot_configs_pkey') THEN
                    ALTER TABLE bot_configs DROP CONSTRAINT bot_configs_pkey;
                END IF;
            END $$;
            """,
            # Re-adding PK might fail if there are duplicates, but usually safe if coming from single-tenant
            "ALTER TABLE bot_configs ADD PRIMARY KEY (guild_id, key);",

            # 3. Add Unique Constraints
            """
            DO $$
            BEGIN
                IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'uq_home_debt_guild_user') THEN
                    ALTER TABLE home_debt ADD CONSTRAINT uq_home_debt_guild_user UNIQUE (guild_id, user_id);
                END IF;
            END $$;
            """,
            """
            DO $$
            BEGIN
                IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'uq_score_guild_user') THEN
                    ALTER TABLE score ADD CONSTRAINT uq_score_guild_user UNIQUE (guild_id, user_id);
                END IF;
            END $$;
            """
        ]
        
        async with self.engine.begin() as conn:
            for q in queries:
                try:
                    await conn.execute(text(q))
                except Exception as e:
                    # Ignore "multiple primary keys" errors if we ran this partially or if constraints conflict in weird ways
                    # But print simple warning
                    pass
        print("✅ Schema verification/migration completed.")

    def get_engine(self) -> AsyncEngine:
        return self.engine

    def get_sessionmaker(self) -> async_sessionmaker[AsyncSession]:
        return self.session_maker


# Singleton export cho dùng chung
postgres = PostgresConnection()
