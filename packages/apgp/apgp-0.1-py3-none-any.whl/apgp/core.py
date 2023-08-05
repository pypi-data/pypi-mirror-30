from pandas import DataFrame
import asyncio

from .db import DB


class Query:
    """Wrapper Class To Abstract Asyncio Functionality

    This class starts with creating the event loop upon
    initialization. From there, every subsequent query
    is constrcuted via the DB class and runs in the event
    loop until completed. A convenience method is also
    supplied to close the event loop. Thus, disallowing
    any further queries.

    Example:

    >>> from apgp import Query
    >>> q = Query('''SELECT * FROM my_table''')
    >>> q.execute()
    >>> q.close()
    """
    def __init__(self, query: str):
        self.query = query
        self._loop = asyncio.get_event_loop()

    def execute(self) -> DataFrame:
        db = DB(self.query)
        values = self._loop.run_until_complete(db.run())
        return correct_columns(values)

    def close(self) -> None:
        self._loop.close()


def correct_columns(vals: list) -> DataFrame:
    """Append Correct Column Names to Asyncpg Records"""
    column_names = [i for i in vals[0].keys()]
    # Convert response
    # asyncpg.Records --> pandas.DataFrame
    data = DataFrame(vals)
    data.columns = column_names
    return data
