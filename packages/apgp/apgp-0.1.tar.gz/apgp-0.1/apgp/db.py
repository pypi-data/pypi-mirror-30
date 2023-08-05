import asyncio
import asyncpg

from .config import _read_config

class DB:
    """Establish Connection & Query Postgres DB

    Queries are sent from `Query` class to initialize.
    From there, all Postgres credentials are read in
    automatically from the `config.yaml` file to
    form the DSN. Once the `execute()` method is called
    from the `Query` class the `run()` method is
    supplied to the event loop.
    """
    def __init__(self, query: str):
        self.query: str = query
        self.dsn: str = _read_config()

    async def run(self) -> list:
        """Async Connection & Querying of Postgres DB"""
        conn = await asyncpg.connect(self.dsn)
        values = await conn.fetch(self.query)
        await conn.close()
        return values
