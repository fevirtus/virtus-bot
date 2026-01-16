import os
import asyncio
import site
import sys

# Add the project directory to sys.path to ensure module resolution works correctly
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import uvicorn
from dotenv import load_dotenv

from bot.core.bot import bot
from web.server import app
from infra.db.postgres import postgres

# Load environment variables
load_dotenv()

async def main():
    print("⏳ Waiting for Database connection...")
    await postgres.wait_for_connection()

    # Ensure schema is migrated (Add missing columns for Multi-Server)
    await postgres.verify_and_migrate_schema()

    # Ensure tables are created
    await postgres.create_tables()

    # Configure Web Server
    app.state.bot = bot
    config = uvicorn.Config(app, host="0.0.0.0", port=8000, log_level="info")
    server = uvicorn.Server(config)

    # Run Bot and Web Server concurrently
    async with bot:
        await asyncio.gather(
            bot.start(os.getenv('BOT_TOKEN')),
            server.serve()
        )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        # Handle graceful shutdown
        pass
