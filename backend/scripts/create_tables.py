import asyncio

from app.db.init_db import create_database_tables


if __name__ == "__main__":
    asyncio.run(create_database_tables())

