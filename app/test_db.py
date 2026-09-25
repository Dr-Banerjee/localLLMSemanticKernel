import asyncio

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.engine import make_url

from config.settings import Settings


async def main():
    settings = Settings()

    url = make_url(settings.databaseUrl)

    print("driver:", url.drivername)
    print("username:", url.username)
    print("host:", url.host)
    print("port:", url.port)
    print("database:", url.database)
    print("password present:", url.password is not None)

    engine = create_async_engine(
        settings.databaseUrl,
        pool_pre_ping=True,
    )

    try:
        async with engine.connect() as connection:
            result = await connection.execute(text("SELECT current_user, current_database()"))
            print("DB connection successful:", result.fetchone())
    finally:
        await engine.dispose()


asyncio.run(main())