# -*- coding: utf-8 -*-
"""
```
License: Apache 2.0

VERSION INFO:
    $Repo: fastapi_pytest
  $Author: Anders Wiklund
    $Date: 2024-04-22 16:14:44
     $Rev: 1
```
"""

# BUILTIN modules
from sys import modules

# Third party modules
from sqlmodel import SQLModel
from sqlalchemy.orm import sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine

connection_url = ('sqlite+aiosqlite:///tracking_test.db'
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
async def get_async_session() -> AsyncSession:
    """ Return an active database session object from the pool.

    Note that this is a DB session generator.

    Returns:
        An active DB session.
    """
    async_session = sessionmaker(
        bind=async_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session


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
