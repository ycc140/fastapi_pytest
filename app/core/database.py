# -*- coding: utf-8 -*-
"""
```
License: Apache 2.0

VERSION INFO:
    $Repo: fastapi_pytest
  $Author: Anders Wiklund
    $Date: 2024-04-29 18:48:17
     $Rev: 11
```
"""

# BUILTIN modules
from sys import modules

# Third party modules
from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine

connection_url = ('sqlite+aiosqlite:///:memory:?cache=shared'
                  if "pytest" in modules
                  else 'sqlite+aiosqlite:///tracking.db')
""" DB connection URL. """

# This param shows the SQL queries in the
# log, perfect during development: echo=True,
async_engine = create_async_engine(
    url=connection_url, future=True,
    connect_args={"check_same_thread": False}
)
""" Create the SQLModel database engine. """


# ---------------------------------------------------------
#
async def create_async_db_tables():
    """ Create the required DB and tables when they don't yet exist. """
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


# ---------------------------------------------------------
#
async def close_async_db():
    """ Close the asynchronous database connection pool. """
    await async_engine.dispose()
